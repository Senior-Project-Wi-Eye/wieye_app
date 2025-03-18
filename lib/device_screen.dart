import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart'; // To use rootBundle for loading assets

class DeviceScreen extends StatefulWidget {
  const DeviceScreen({super.key, required this.title});
  final String title;

  @override
  _DeviceScreenState createState() => _DeviceScreenState();
}

class _DeviceScreenState extends State<DeviceScreen> {
  List<Map<String, dynamic>> devices = [];

  // Assign icons to devices based on the OS
  IconData getDeviceIcon(String type) {
    if (type.toLowerCase().contains('windows')) {
      return Icons.laptop_windows;
    } else if (type.toLowerCase().contains('android')) {
      return Icons.phone_android;
    } else if (type.toLowerCase().contains('ios') || type.toLowerCase().contains('apple')) {
      return Icons.phone_iphone;
    } else if (type.toLowerCase().contains('linux')) {
      return Icons.laptop;
    } else if (type.toLowerCase().contains('mac')) {
      return Icons.desktop_mac;
    } else {
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

    // Load detailed result from 'lib' directory
    final detailData = await rootBundle.loadString('lib/DetailedResult.json');
    final detailJson = json.decode(detailData);
    final List detailHosts = detailJson['hosts'];

    // Merge IP, OS, and Detail results
    List<Map<String, dynamic>> devicesList = [];
    for (var ipHost in ipHosts) {
      String ip = ipHost['host'];
      String status = ipHost['status'];

      // Find the OS data for the matching IP
      var osHost = osHosts.firstWhere(
            (os) => os['host'] == ip,
        orElse: () => {'os': 'Unknown'},
      );
      String os = osHost['os'] ?? 'Unknown';

      // Find detailed data for the matching IP
      var detailHost = detailHosts.firstWhere(
            (detail) => detail['host'] == ip,
        orElse: () => {'ports': [], 'services': []},
      );

      List ports = detailHost['ports'] ?? [];
      List services = detailHost['services'] ?? [];

      devicesList.add({
        "ip": ip,
        "status": status,
        "os": os,
        "ports": ports,
        "services": services,
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

  void _showDetailDialog(BuildContext context, Map<String, dynamic> device) {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: Text('Device Details: ${device['ip']}'),
          content: SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Text('OS: ${device['os']}', style: const TextStyle(fontWeight: FontWeight.bold)),
                const SizedBox(height: 8),

                if (device['ports'].isNotEmpty) ...[
                  const Text('Ports:', style: TextStyle(fontWeight: FontWeight.bold)),
                  const SizedBox(height: 4),
                  ...device['ports'].map<Widget>((port) => Padding(
                    padding: const EdgeInsets.only(left: 8.0, bottom: 4.0),
                    child: Text('• $port'),
                  )).toList(),
                  const SizedBox(height: 8),
                ],

                if (device['services'].isNotEmpty) ...[
                  const Text('Services:', style: TextStyle(fontWeight: FontWeight.bold)),
                  const SizedBox(height: 4),
                  ...device['services'].map<Widget>((service) => Padding(
                    padding: const EdgeInsets.only(left: 8.0, bottom: 4.0),
                    child: Text('• $service'),
                  )).toList(),
                ],
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('Close'),
            ),
          ],
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(widget.title)),
      body: devices.isEmpty
          ? const Center(child: CircularProgressIndicator())
          : ListView.builder(
        itemCount: devices.length,
        itemBuilder: (context, index) {
          var device = devices[index];
          // Determine the color based on the device status
          Color statusColor = device['status'].toString().toLowerCase() == 'up' ? Colors.green : Colors.red;

          return Card(
            child: ListTile(
              leading: Icon(getDeviceIcon(device["os"] ?? 'unknown'), size: 40),
              title: Text("IP: ${device['ip']}"),
              subtitle: Text("OS: ${device['os']} - Status: ${device['status']}"),
              trailing: Icon(Icons.circle, color: statusColor, size: 14),
              onTap: () => _showDetailDialog(context, device),
            ),
          );
        },
      ),
    );
  }
}