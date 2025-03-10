import 'package:flutter/material.dart';
import 'noti_service.dart';
import 'login_screen.dart';
import 'home_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  NotiService().intiNotification();

  runApp(const WieyeApp());
}

class WieyeApp extends StatelessWidget {
  const WieyeApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.tealAccent),
      ),
      debugShowCheckedModeBanner: false,
      home: HomeScreen(title: "Home"),
      //home: LoginScreen(), // testing notifications
    );
  }
}
