import 'package:flutter_local_notifications/flutter_local_notifications.dart';

class NotiService {
  final notificationsPlugin = FlutterLocalNotificationsPlugin();
  static final NotiService _instance = NotiService._internal();
  bool _isInitialized = false;
  bool get isInitialized => _isInitialized;

  factory NotiService() {
    return _instance;
  }

  NotiService._internal();

  // INITIALIZE
  Future<void> initNotification() async {
    if (_isInitialized) return; // prevent re-initalization

    // prepare android init settings
    const initSettingsAndroid =
      AndroidInitializationSettings('@mipmap/android_logo');
   // const initSettingsWindows = WindowsInitializationSettings();

    // inti settings
    const intiSettings = InitializationSettings(
        android: initSettingsAndroid,
       // windows: initSettingsWindows,
    );

    // initizalize the  plugin!
    await notificationsPlugin.initialize(intiSettings);

    _isInitialized = true;  // Mark as initialized
  }

  // NOTIFICATIONS DETAIL SETUP
  NotificationDetails notificationDetails() {
    return const NotificationDetails(
      android: AndroidNotificationDetails(
          'network_channel_id',
          'Network Notifications',
          channelDescription: 'Network Notifications Channel',
          importance: Importance.max,
          priority: Priority.high,
      ),
    );
  }

  // SHOW NOTIFICATION
  Future<void> showNotification({
    int id = 0,
    String? title,
    String? body,
  }) async {
    if (!_isInitialized) {
      print('Notification plugin not initialized yet!');
      await initNotification();  // Try to initialize if not done
    }

    return notificationsPlugin.show(
      id,
      title,
      body,
      notificationDetails(),
    );
  }
// ON NOTi TAP

}