import 'package:flutter/material.dart';
import 'main.dart';
import 'noti_history.dart';
import 'noti_service.dart';
import 'device_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key, required this.title});
  final String title;

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _selectedIndex = 0;

  void _onItemTapped(int index) {
    setState(() {
      _selectedIndex = index;
    });
  }

  // List of screen
  static final List<Widget> _screens = <Widget>[
    const Center(child: Text('Home Screen')),
    const DeviceScreen(title: "Devices"),
  ];

  @override
  void initState() {
    super.initState();
    // Set context after the first build
    WidgetsBinding.instance.addPostFrameCallback((_) {
      globalNotiService.setContext(context);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        title: Text(widget.title),
        actions: [
          IconButton(
            icon: const Icon(Icons.notifications),
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
              child: _screens[_selectedIndex], // Your existing screen widget
            ),
            ElevatedButton(
              onPressed: () async {
                // Wait for initialization to complete before showing notification
                if (NotiService().isInitialized) {
                  globalNotiService.showNotification(
                    title: "Wi-Eye",
                    body: "Warning Malware Detected!",
                  );
                } else {
                  print("Notification plugin not initialized yet!");
                }
              },
              child: const Text("Send Notification"),
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
