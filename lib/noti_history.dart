import 'package:flutter/material.dart';
import 'package:intl/intl.dart'; // For formatting date & time
import 'noti_service.dart';

class NotificationHistoryScreen extends StatefulWidget {
  const NotificationHistoryScreen({super.key});

  @override
  State<NotificationHistoryScreen> createState() => _NotificationHistoryScreenState();
}

class _NotificationHistoryScreenState extends State<NotificationHistoryScreen> {
  List<MalwareNotification> _notifications = [];

  @override
  void initState() {
    super.initState();
    _loadHistory();
  }

  void _loadHistory() {
    setState(() {
      _notifications = NotiService().notificationHistory.reversed.toList();
    });
  }

  Future<void> _clearNotifications() async {
    await NotiService().clearHistory();
    setState(() {
      _notifications.clear();
    });

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text("Notification history cleared")),
    );
  }

  String _formatTimestamp(DateTime timestamp) {
    return DateFormat('MMM d, HH:mm').format(timestamp); // Example: Apr 22, 14:30
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Notification History'),
        actions: [
          if (_notifications.isNotEmpty)
            IconButton(
              icon: const Icon(Icons.delete),
              tooltip: "Clear History",
              onPressed: _clearNotifications,
            ),
        ],
      ),
      body: _notifications.isEmpty
          ? const Center(child: Text('No alerts yet.'))
          : ListView.builder(
        itemCount: _notifications.length,
        itemBuilder: (context, index) {
          final noti = _notifications[index];
          return Card(
            margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            child: ListTile(
              leading: Icon(
                noti.body.toLowerCase().contains("blocked")
                    ? Icons.block
                    : Icons.warning,
                color: noti.body.toLowerCase().contains("blocked")
                    ? Colors.orange
                    : Colors.red,
              ),
              title: Text(noti.title),
              subtitle: Text(noti.body),
              trailing: Text(
                _formatTimestamp(noti.timestamp),
                style: const TextStyle(fontSize: 12),
              ),
            ),
          );
        },
      ),
    );
  }
}
