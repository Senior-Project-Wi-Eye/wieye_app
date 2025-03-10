import 'package:flutter_local_notifications/flutter_local_notifications.dart';

class NotiService {
  final notificationsPlugin = FlutterLocalNotificationsPlugin();

  bool _isInitialized = false;

  bool get isInitialized => _isInitialized;

  // INITIALIZE
  Future<void> intiNotification() async {
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

  } ) async{
    return notificationsPlugin.show(id,
      title,
      body,
      const NotificationDetails(),
    );
  }
  // ON NOTi TAP

}