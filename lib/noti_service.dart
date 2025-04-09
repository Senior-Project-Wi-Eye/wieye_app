import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'dart:io' show Platform;
import 'package:flutter/material.dart';
import 'dart:async';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'current_user.dart';

class NotiService {
  final notificationsPlugin = FlutterLocalNotificationsPlugin();
  static final NotiService _instance = NotiService._internal();
  bool _isInitialized = false;
  bool get isInitialized => _isInitialized;

  BuildContext? _context;
  BuildContext? get context => _context;
  Timer? _malwareTimer;

  final Map<String, List<MalwareNotification>> _userHistories = {};

  List<MalwareNotification> get notificationHistory {
    final user = currentUserEmail ?? 'guest';
    return _userHistories[user] ?? [];
  }

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

  // START Malware check
  void startMalwareCheck() {
    _malwareTimer ??= Timer.periodic(const Duration(seconds: 5), (timer) async {
      try {
        final res = await http.get(Uri.parse('http://10.15.159.179:5000/malware-alert'));
        final data = jsonDecode(res.body);

        // Check for attack notifications
        if (data["malware"] == true) {
          final String info = data["info"] ?? "Malicious Traffic Detected!";
          showNotification(title: "Malware Detected", body: info);
        }

        // Check for new devices or other custom notifications
        final deviceRes = await http.get(Uri.parse('http://10.15.159.179:5000/notification-feed'));
        final List<dynamic> alerts = jsonDecode(deviceRes.body);

        for (var alert in alerts) {
          showNotification(title: alert["title"], body: alert["body"]);
        }

      } catch (e) {
        print("Failed to check malware alert: $e");
      }
    });
  }

  // Stop Malware Check
  void stopMalwareCheck() {
    _malwareTimer?.cancel();
    _malwareTimer = null;
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

    // Save to history (common to all platforms)
    if (title != null && body != null) {
      final user = currentUserEmail ?? 'guest';
      final noti = MalwareNotification(
        title: title,
        body: body,
        timestamp: DateTime.now(),
      );
      _userHistories.putIfAbsent(user, () => []).add(noti);
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

class MalwareNotification {
  final String title;
  final String body;
  final DateTime timestamp;

  MalwareNotification({
    required this.title,
    required this.body,
    required this.timestamp,
  });
}
