import 'package:flutter/material.dart';
import 'noti_service.dart';

class NotificationHistoryScreen extends StatelessWidget {
  const NotificationHistoryScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final notifications = NotiService().notificationHistory;

    return Scaffold(
      appBar: AppBar(title: const Text('Notification History')),
      body: notifications.isEmpty
          ? const Center(child: Text('No alerts yet.'))
          : ListView.builder(
        itemCount: notifications.length,
        itemBuilder: (context, index) {
          final noti = notifications[index];
          return Card(
            margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            child: ListTile(
              leading: const Icon(Icons.warning, color: Colors.red),
              title: Text(noti.title),
              subtitle: Text(noti.body),
              trailing: Text(
                "${noti.timestamp.hour}:${noti.timestamp.minute.toString().padLeft(2, '0')}",
                style: const TextStyle(fontSize: 12),
              ),
            ),
          );
        },
      ),
    );
  }
}
