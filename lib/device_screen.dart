import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart'; // To use rootBundle for loading assets

bool isScanning = false;

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
    const apiUrl = 'http://10.15.159.179:5000/get-all-results';

    try {
      final response = await http.get(Uri.parse(apiUrl));

      if (response.statusCode == 200) {
        final result = jsonDecode(response.body);

        final ipJson = jsonDecode(result['ip_result']);
        final osJson = jsonDecode(result['os_result']);
        final detailJson = jsonDecode(result['detailed_result']);

        final List ipHosts = ipJson['hosts'];
        final List osHosts = osJson['hosts'];
        final List detailHosts = detailJson['hosts'];

        List<Map<String, dynamic>> devicesList = [];

        for (var ipHost in ipHosts) {
          String ip = ipHost['host'];
          String status = ipHost['status'];

          var osHost = osHosts.firstWhere(
                (os) => os['host'] == ip,
            orElse: () => {'os': 'Unknown'},
          );
          String os = osHost['os'] ?? 'Unknown';

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
      } else {
        throw Exception('Failed to load data: ${response.statusCode}');
      }
    } catch (e) {
      print('Error loading data: $e');
    }
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
            TextButton(
              onPressed: () {
                Navigator.of(context).pop(); // Close the dialog
                scanDevice(device['ip']);    // Trigger scan
              },
              child: const Text('Scan'),
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

  Future<void> scanDevice(String ip) async {
    const apiUrl = 'http://10.15.159.179:5000/scan';

    setState(() {
      isScanning = true;
    });

    try {
      final response = await http.post(
        Uri.parse(apiUrl),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'ip': ip}),
      );

      if (response.statusCode == 200) {
        final result = jsonDecode(response.body);
        final newHost = result['hosts'][0];

        final updatedDevices = devices.map((device) {
          if (device['ip'] == newHost['host']) {
            return {
              ...device,
              'status': newHost['status'],
              'os': newHost['os'],
              'ports': newHost['ports'],
              'services': newHost['services'],
            };
          }
          return device;
        }).toList();

        setState(() {
          devices = updatedDevices;
        });

        showDialog(
          context: context,
          builder: (_) => AlertDialog(
            title: Text("Scan Complete"),
            content: Text("Device ${newHost['host']} updated."),
          ),
        );
      } else {
        showDialog(
          context: context,
          builder: (_) => AlertDialog(
            title: Text("Scan Failed"),
            content: Text("Server error: ${response.body}"),
          ),
        );
      }
    } catch (e) {
      showDialog(
        context: context,
        builder: (_) => AlertDialog(
          title: Text("Error"),
          content: Text("Could not connect to scanner server."),
        ),
      );
    } finally {
      setState(() {
        isScanning = false;
      });
    }
  }

}