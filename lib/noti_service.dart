import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'dart:io' show Platform;
import 'package:flutter/material.dart';

class NotiService {
  final notificationsPlugin = FlutterLocalNotificationsPlugin();
  static final NotiService _instance = NotiService._internal();
  bool _isInitialized = false;
  bool get isInitialized => _isInitialized;

  BuildContext? _context;
  void setContext(BuildContext context) {
    _context = context;
  }

  factory NotiService() {
    return _instance;
  }

  NotiService._internal();

  // INITIALIZE
  Future<void> initNotification() async {
    if (_isInitialized) return; // prevent re-initalization

    if (Platform.isAndroid) {
      // prepare android init settings
      const initSettingsAndroid = AndroidInitializationSettings('@mipmap/ic_launcher');

      // inti settings
      const initSettings = InitializationSettings(
        android: initSettingsAndroid,
      );

      // initizalize the  plugin!
      await notificationsPlugin.initialize(initSettings);
    }

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
      await initNotification();
    }

    if (Platform.isAndroid) {
      // Android notification
      const androidDetails = AndroidNotificationDetails(
        'network_channel_id',
        'Network Notifications',
        channelDescription: 'Network Notifications Channel',
        importance: Importance.max,
        priority: Priority.high,
      );

      const details = NotificationDetails(android: androidDetails);

      return notificationsPlugin.show(id, title, body, details);
    }
    else if (Platform.isWindows && _context != null) {
      // Windows fallback - show a snackbar or dialog
      ScaffoldMessenger.of(_context!).showSnackBar(
        SnackBar(
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              if (title != null)
                Text(
                  title,
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
              if (body != null)
                Text(body),
            ],
          ),
          duration: const Duration(seconds: 5),
          action: SnackBarAction(
            label: 'Dismiss',
            onPressed: () {},
          ),
        ),
      );
    }
  }
}