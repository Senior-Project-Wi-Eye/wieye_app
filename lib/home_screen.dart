import 'package:flutter/material.dart';
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
    const DeviceScreen(),
  ];

  @override
  void initState() {
    super.initState();
    WidgetsFlutterBinding.ensureInitialized();
    NotiService().intiNotification();
  }
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        title: Text(widget.title),
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
                  await NotiService().showNotification(
                    title: "Wi-Eye",
                    body: "Body",
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
      ),
    );
  }

}
