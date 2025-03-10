import 'package:flutter/material.dart';

// Show user their devices and it's information
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