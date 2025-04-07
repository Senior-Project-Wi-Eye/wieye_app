import 'package:flutter/material.dart';
import 'noti_service.dart';
import 'login_screen.dart';
import 'home_screen.dart';

// Create a global instance that can be accessed anywhere
final globalNotiService = NotiService();

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  try {
    await globalNotiService.initNotification();
    print('Notification service initialized');
  } catch (e) {
    print('Error initializing notifications: $e');
  }

  NotiService().startMalwareCheck();

  runApp(const WieyeApp());
}

class WieyeApp extends StatelessWidget {
  const WieyeApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.lightBlueAccent),
      ),
      debugShowCheckedModeBanner: false,
      home: HomeScreen(title: ""),
    );
  }
}