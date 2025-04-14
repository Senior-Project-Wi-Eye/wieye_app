import 'dart:async';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'main.dart';
import 'dart:convert';
import 'noti_history.dart';
import 'device_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key, required this.title});
  final String title;

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _selectedIndex = 0;

  List<String> _logs = [];

  void _onItemTapped(int index) {
    setState(() {
      _selectedIndex = index;
    });
  }


  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      globalNotiService.setContext(context);
      _startLogPolling();
    });
  }

  void _startLogPolling() {
    Timer.periodic(Duration(seconds: 2), (timer) async {
      final res = await http.get(Uri.parse('http://10.15.159.179:5000/scan-log'));
      if (res.statusCode == 200) {
        final List<dynamic> jsonLogs = jsonDecode(res.body);
        setState(() {
          _logs = List<String>.from(jsonLogs.reversed);
        });
      }
    });
  }

  Widget _buildScanLogScreen() {
    return Padding(
      padding: const EdgeInsets.all(12.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            "Live Scan Log",
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 12),
          Expanded(
            child: Container(
              decoration: BoxDecoration(
                color: Colors.black,
                borderRadius: BorderRadius.circular(10),
              ),
              padding: const EdgeInsets.all(10),
              child: ListView.builder(
                itemCount: _logs.length,
                reverse: true,
                itemBuilder: (context, index) {
                  return Text(
                    _logs[index],
                    style: const TextStyle(
                      color: Colors.greenAccent,
                      fontFamily: 'monospace',
                      fontSize: 13,
                    ),
                  );
                },
              ),
            ),
          ),
        ],
      ),
    );
  }


  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Color(0xFF0D1B2A),
        title: Row(
          children: [
            Image.asset('assets/Icon-48.png', height: 30),
            const SizedBox(width: 2),
            Image.asset('assets/wordlogo.png', height: 25),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(
              Icons.notifications,
              color: Colors.lightBlueAccent,
            ),
            onPressed: () {
              Navigator.of(context).push(
                MaterialPageRoute(
                  builder: (context) => const NotificationHistoryScreen(),
                ),
              );
            },
          ),
        ],
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Wrap the screen in Expanded to take up available space
            Expanded(
              child: _selectedIndex == 0
                  ? _buildScanLogScreen()
                  : const DeviceScreen(title: "Devices"),
            ),
          ],
        ),
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _selectedIndex,
        onTap: _onItemTapped,
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.home),
            label: 'Home',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.devices),
            label: 'Device',
          ),
        ],
        backgroundColor: Colors.black, // Set background color to black
        selectedItemColor: Colors.lightBlueAccent, // Set selected item color to white
        unselectedItemColor: Colors.grey, // Set unselected item color to grey
        type: BottomNavigationBarType.fixed, // Ensure the background color is applied
      ),
    );
  }

}
