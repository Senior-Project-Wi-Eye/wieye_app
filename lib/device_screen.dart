import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart'; // To use rootBundle for loading assets

class DeviceScreen extends StatefulWidget {
  const DeviceScreen({super.key});

  @override
  _DeviceScreenState createState() => _DeviceScreenState();
}

class _DeviceScreenState extends State<DeviceScreen> {
  List<Map<String, String>> devices = [];

  // Assign icons to devices based on the OS
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

  // Load the JSON files and parse them
  Future<void> loadData() async {
    // Load IP result from 'lib' directory
    final ipData = await rootBundle.loadString('lib/IPResult.json');
    final ipJson = json.decode(ipData);
    final List ipHosts = ipJson['hosts'];

    // Load OS result from 'lib' directory
    final osData = await rootBundle.loadString('lib/OSResult.json');
    final osJson = json.decode(osData);
    final List osHosts = osJson['hosts'];

    // Merge IP and OS results
    List<Map<String, String>> devicesList = [];
    for (var ipHost in ipHosts) {
      String ip = ipHost['host'];
      String status = ipHost['status'];

      // Find the OS data for the matching IP
      var osHost = osHosts.firstWhere(
            (os) => os['host'] == ip,
        orElse: () => {'os': 'Unknown'},
      );
      String os = osHost['os'] ?? 'Unknown';

      devicesList.add({
        "ip": ip,
        "status": status,
        "os": os,
      });
    }

    setState(() {
      devices = devicesList;
    });
  }

  @override
  void initState() {
    super.initState();
    loadData();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Devices")),
      body: devices.isEmpty
          ? const Center(child: CircularProgressIndicator())
          : ListView.builder(
        itemCount: devices.length,
        itemBuilder: (context, index) {
          var device = devices[index];
          // Determine the color based on the device status
          Color statusColor = device['status'] == 'up' ? Colors.green : Colors.red;

          return Card(
            child: ListTile(
              leading: Icon(getDeviceIcon(device["os"] ?? 'unknown'), size: 40),
              title: Text("IP: ${device['ip']}"),
              subtitle: Text("OS: ${device['os']} - Status: ${device['status']}"),
              trailing: Icon(Icons.circle, color: statusColor, size: 14), // Change color based on status
            ),
          );
        },
      ),
    );
  }
}
