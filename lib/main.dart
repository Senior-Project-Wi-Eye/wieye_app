import 'package:flutter/material.dart';

void main() {
  runApp(const WieyeApp());
}

class WieyeApp extends StatelessWidget {
  const WieyeApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.blueAccent),
      ),
      home: const HomeScreen(title: 'Wi-Eye Demo'),
    );
  }
}

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
    const InfoScreen(),
  ];

  // Navigation Bar: How app move bettween screen
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        title: Text(widget.title),
      ),
      body: Center(
        child: _screens[_selectedIndex],
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
          BottomNavigationBarItem(
            icon: Icon(Icons.info),
            label: 'Info',
          ),
        ],
      ),
    );
  }
}

class DeviceScreen extends StatelessWidget {
  const DeviceScreen({super.key});

  // List of decives on network
  final List<Map<String, String>> devices = const [
    {"name": "Windows", "type": "monitor", "ip": "10.0.0.21"},
    {"name": "iPhone", "type": "smartphone", "ip": "10.0.0.22"},
    {"name": "Laptop", "type": "laptop", "ip": "10.0.0.23"},
    {"name": "Android", "type": "smartphone", "ip": "10.0.0.24"},
    {"name": "iPad", "type": "tablet", "ip": "10.0.0.25"},
    {"name": "Unidentified Device", "type": "unknown", "ip": "10.0.0.26"},
  ];

  // Assign icons to devices
  IconData getDeviceIcon(String type) {
    switch (type) {
      case "smartphone":
        return Icons.smartphone;
      case "monitor":
        return Icons.monitor;
      case "laptop":
        return Icons.laptop;
      case "tablet":
        return Icons.tablet;
      case "unknown":
        return Icons.device_unknown;
      default:
        return Icons.devices;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Devices")),
      body: Column(
        children: [
          // Device List
          Expanded(
            child: ListView.builder(
              itemCount: devices.length,
              itemBuilder: (context, index) {
                var device = devices[index];
                return Card(
                  child: ListTile(
                    leading: Icon(getDeviceIcon(device["type"]!), size: 40),
                    title: Text(device["name"]!),
                    subtitle: Text("IP Address: ${device["ip"]}"),
                    trailing: const Icon(Icons.circle, color: Colors.green, size: 14),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}


class InfoScreen extends StatelessWidget {
  const InfoScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Center(child: Text('Info'))),
      body: const Center(
        child: Text('This is the Info Screen'),
      ),
    );
  }
}
