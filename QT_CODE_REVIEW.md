# 🔍 Комплексная проверка Qt CNC Pult приложения

## 📊 Статус: ⚠️ ТРЕБУЮТСЯ ИСПРАВЛЕНИЯ

---

## 🔴 КРИТИЧЕСКИЕ ПРОБЛЕМЫ

### 1. Memory Leak при переподключении (mainwindow.cpp)

**Проблема:**
```cpp
// Строки 159-164 в mainwindow.cpp
void MainWindow::onConnectClicked()
{
    if (m_socket->state() == QAbstractSocket::UnconnectedState) {
        // Сокет переиспользуется, но нет явного reset
        m_socket->connectToHost(m_hostEdit->text(), 
                               static_cast<quint16>(m_portSpin->value()));
    }
}
```

**Почему это проблема:**
- При быстрых переподключениях буфер `m_rxBuffer` может содержать старые данные
- Нет проверки на успешность подключения перед отправкой команд

**Решение:**
```cpp
void MainWindow::onConnectClicked()
{
    if (m_socket->state() == QAbstractSocket::UnconnectedState) {
        m_rxBuffer.clear(); // ✅ Очищаем старый буфер
        appendLog(QString("Подключение к %1:%2 ...")
                  .arg(m_hostEdit->text()).arg(m_portSpin->value()), true);
        m_socket->connectToHost(m_hostEdit->text(), 
                               static_cast<quint16>(m_portSpin->value()));
        m_connectBtn->setEnabled(false);
        m_connectBtn->setText("Подключение...");
    } else if (m_socket->state() == QAbstractSocket::ConnectedState) {
        // ✅ Явное отключение с ожиданием
        m_socket->disconnectFromHost();
        if (m_socket->state() != QAbstractSocket::UnconnectedState) {
            m_socket->waitForDisconnected(1000);
        }
    }
}
```

---

### 2. Переполнение буфера приёма (mainwindow.cpp)

**Проблема:**
```cpp
void MainWindow::onSocketReadyRead()
{
    m_rxBuffer.append(m_socket->readAll()); // ❌ Нет проверки размера
    // Если сетевое соединение зависнет, буфер может вырасти до гигабайт!
}
```

**Решение:**
```cpp
void MainWindow::onSocketReadyRead()
{
    QByteArray data = m_socket->readAll();
    
    // ✅ Защита от переполнения
    const int MAX_BUFFER_SIZE = 1024 * 1024; // 1 MB
    if (m_rxBuffer.size() + data.size() > MAX_BUFFER_SIZE) {
        appendLog("⚠️ ОШИБКА: Переполнение буфера приёма", false);
        m_rxBuffer.clear();
        m_socket->disconnectFromHost();
        setMachineMode(MachineMode::Alarm);
        return;
    }
    
    m_rxBuffer.append(data);

    int newlineIndex;
    while ((newlineIndex = m_rxBuffer.indexOf('\n')) != -1) {
        // ... остальной код
    }
}
```

---

### 3. Утечка памяти OpenGL контекста (toolpathwidget.cpp)

**Проблема:**
```cpp
ToolpathWidget::ToolpathWidget(QWidget *parent)
    : QOpenGLWidget(parent)
{
    setMinimumSize(400, 350);
    setupOverlayUI();
    // ❌ Нет явного управления контекстом при удалении
}

MainWindow::~MainWindow()
{
    if (m_toolpathWidget) {
        m_toolpathWidget->doneCurrent(); // Вызывается слишком поздно
    }
}
```

**Решение:**
```cpp
// toolpathwidget.h - добавить
class ToolpathWidget : public QOpenGLWidget, protected QOpenGLFunctions
{
    // ...
public:
    ~ToolpathWidget() override;
    
private:
    GLuint m_vao = 0, m_vbo = 0; // Явное управление ресурсами
};

// toolpathwidget.cpp
ToolpathWidget::~ToolpathWidget()
{
    makeCurrent(); // ✅ Активируем контекст перед удалением ресурсов
    
    if (m_vao) glDeleteVertexArrays(1, &m_vao);
    if (m_vbo) glDeleteBuffers(1, &m_vbo);
    
    doneCurrent();
}

void ToolpathWidget::initializeGL()
{
    initializeOpenGLFunctions();
    glClearColor(0.12f, 0.14f, 0.16f, 1.0f);
    glEnable(GL_DEPTH_TEST);
    glEnable(GL_LINE_SMOOTH);
    glEnable(GL_POINT_SMOOTH);
    glEnable(GL_POLYGON_SMOOTH);
    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST);
    glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST);
}
```

---

### 4. Гонка данных в Python симуляторе (mock_stm32_server.py)

**Проблема:**
```python
def client_thread(conn, addr):
    # ...
    while True:
        # ❌ ОПАСНО: machine.events может изменяться из simulation_loop()
        with machine.lock:
            pending = machine.events[:] # Хорошо
            machine.events.clear()
        for ev in pending:
            conn.sendall((ev + "\n").encode("utf-8"))
```

**Решение:**
```python
# Использовать queue вместо простого списка
import queue

class Machine:
    def __init__(self):
        # ...
        self.event_queue = queue.Queue(maxsize=100) # ✅ Потокобезопасная очередь
    
    def push_event(self, text):
        try:
            self.event_queue.put_nowait(text)
        except queue.Full:
            print(f"⚠️ Event queue overflow: {text}")

def client_thread(conn, addr):
    # ...
    try:
        # Обработка очереди событий
        while True:
            try:
                event = machine.event_queue.get_nowait()
                conn.sendall((event + "\n").encode("utf-8"))
            except queue.Empty:
                pass
    except (ConnectionResetError, BrokenPipeError):
        pass
```

---

## ⚠️ ВАЖНЫЕ БАГИ

### 5. Неправильная обработка пустой комбобокса камеры (camerapanel.cpp)

**Проблема:**
```cpp
void CameraPanel::onStartStopClicked()
{
    // ...
    const int idx = m_deviceCombo->currentIndex();
    if (devices.isEmpty() || idx < 0 || idx >= devices.size()) {
        // ❌ Ошибка может быть скрыта от пользователя
        QMessageBox::warning(this, "Камера", "Не выбрано ни одной камеры.");
        m_startStopBtn->setChecked(false);
        return;
    }
}
```

**Решение:**
```cpp
void CameraPanel::refreshDeviceList()
{
    m_deviceCombo->clear();
    const QList<QCameraDevice> devices = QMediaDevices::videoInputs();
    
    if (devices.isEmpty()) {
        m_deviceCombo->addItem("— Камеры не найдены —");
        m_deviceCombo->setEnabled(false);
        m_startStopBtn->setEnabled(false);
        m_statusLabel->setText("Камеры не найдены");
        m_statusLabel->setStyleSheet("color: #d9534f;");
        return;
    }
    
    m_deviceCombo->setEnabled(true);
    m_startStopBtn->setEnabled(true);
    m_statusLabel->setStyleSheet("color: gray;");
    
    for (const QCameraDevice &dev : devices) {
        m_deviceCombo->addItem(dev.description(), QVariant::fromValue(dev));
    }
}
```

---

### 6. Отсутствие проверки состояния перед отправкой команд

**Проблема:**
```cpp
void MainWindow::sendLine(const QString &line)
{
    if (m_socket->state() != QAbstractSocket::ConnectedState) {
        return; // ❌ Молчаливо игнорируем ошибку
    }
    m_socket->write((line + "\n").toUtf8());
}
```

**Решение:**
```cpp
void MainWindow::sendLine(const QString &line)
{
    if (m_socket->state() != QAbstractSocket::ConnectedState) {
        appendLog("⚠️ Ошибка: Станок не подключен. Команда отклонена: " + line, true);
        QMessageBox::warning(this, "Ошибка соединения", 
                           "Невозможно отправить команду: соединение со станком разорвано.");
        return;
    }
    
    qint64 written = m_socket->write((line + "\n").toUtf8());
    if (written <= 0) {
        appendLog("❌ Ошибка: Не удалось отправить команду", true);
    }
}
```

---

### 7. G-код парсер игнорирует модальные команды (toolpathwidget.cpp)

**Проблема:**
```cpp
void ToolpathWidget::parseGCodeLine(const QString &line, QVector3D &currentPos)
{
    // ...
    int gCode = -1;
    
    // Если gCode не найден, остаётся -1
    bool isRapid = (gCode == 0); // ❌ false, даже если это G0
}
```

**Решение:**
```cpp
class ToolpathWidget : public QOpenGLWidget, protected QOpenGLFunctions
{
private:
    int m_modalGCode = 1; // ✅ Сохраняем модальную команду
};

void ToolpathWidget::parseGCodeLine(const QString &line, QVector3D &currentPos)
{
    // ...
    QRegularExpression rx("([GXYZABCIJK])([+-]?\\d*\\.?\\d+)");
    QRegularExpressionMatchIterator iter = rx.globalMatch(line);

    double x = currentPos.x(), y = currentPos.y(), z = currentPos.z();
    int gCode = m_modalGCode; // ✅ Используем модальное значение
    
    while (iter.hasNext()) {
        QRegularExpressionMatch m = iter.next();
        QString axis = m.captured(1);
        double val = m.captured(2).toDouble();
        
        if (axis == "G") {
            gCode = static_cast<int>(val);
            m_modalGCode = gCode; // ✅ Запоминаем новую модальную команду
        }
        // ...
    }
    
    bool moved = (currentPos.x() != x || currentPos.y() != y || currentPos.z() != z);
    if (!moved) return;

    bool isRapid = (gCode == 0); // ✅ Теперь правильно
    // ...
}
```

---

## 🚨 ПРОБЛЕМЫ ПРОИЗВОДИТЕЛЬНОСТИ

### 8. Неоптимальная обновление UI при быстрых сообщениях

**Проблема:**
```cpp
m_logEdit->appendPlainText(ts + " " + prefix + text);
// ❌ Каждый append вызывает перерисовку
```

**Решение:**
```cpp
class MainWindow : public QMainWindow
{
private:
    QTimer *m_uiUpdateTimer = nullptr;
    QStringList m_pendingLogs;
};

void MainWindow::appendLog(const QString &text, bool outgoing)
{
    const QString ts = QDateTime::currentDateTime().toString("HH:mm:ss.zzz");
    const QString prefix = outgoing ? ">> " : "<< ";
    m_pendingLogs.append(ts + " " + prefix + text);
    
    // ✅ Обновляем UI раз в 100ms вместо после каждого сообщения
    if (!m_uiUpdateTimer->isActive()) {
        m_uiUpdateTimer->start(100);
    }
}

void MainWindow::flushPendingLogs()
{
    if (!m_pendingLogs.isEmpty()) {
        m_logEdit->appendPlainText(m_pendingLogs.join("\n"));
        m_pendingLogs.clear();
    }
}
```

---

### 9. Не используется многопоточность для I/O

**Проблема:**
```cpp
// UI замерзает при медленном сетевом соединении
void MainWindow::onSocketReadyRead()
{
    // ❌ Вся обработка в главном потоке
}
```

**Решение:**
```cpp
// Использовать QThread для сетевых операций
class NetworkWorker : public QObject
{
    Q_OBJECT
public slots:
    void processData(const QByteArray &data);
signals:
    void dataProcessed(const QString &line);
};
```

---

## ✅ РЕКОМЕНДАЦИИ

### Улучшения в коде:

| Проблема | Приоритет | Сложность | Время |
|----------|-----------|-----------|-------|
| Memory leak буфера | 🔴 КРИТИЧНО | 1/5 | 5 мин |
| Защита от переполнения | 🔴 КРИТИЧНО | 2/5 | 10 мин |
| OpenGL контекст | 🟠 ВАЖНО | 2/5 | 15 мин |
| G-код модальность | 🟠 ВАЖНО | 2/5 | 20 мин |
| Обработка ошибок | 🟡 СРЕДНЕ | 1/5 | 10 мин |
| Производительность UI | 🟡 СРЕДНЕ | 3/5 | 30 мин |
| Потокобезопасность | 🟠 ВАЖНО | 3/5 | 45 мин |

---

## 📝 ИТОГИ

✅ **Что хорошо:**
- Архитектура модульная и понятная
- Использование сигналов/слотов
- Хорошее разделение на UI слои
- Поддержка 6 осей

⚠️ **Что нужно исправить:**
- Управление памятью при сокетах
- Защита от переполнения буфера
- Обработка ошибок сети
- G-код парсер не полный

🚀 **Что нужно добавить:**
- Многопоточность для I/O
- Батч-обновление UI
- Тестирование граничных случаев
- Логирование ошибок в файл
- Отладочный режим

---

## 🔧 БЫСТРЫЕ ИСПРАВЛЕНИЯ

Готов создать файлы с исправлениями:
1. `mainwindow_fixed.cpp` — исправленная версия
2. `toolpathwidget_fixed.cpp` — с модальностью G-кода
3. `mock_stm32_server_fixed.py` — с потокобезопасностью
4. `networkworker.cpp/h` — отдельный поток для сети

Хотите, чтобы я создал эти файлы?
