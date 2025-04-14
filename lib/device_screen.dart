import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart'; // To use rootBundle for loading assets
import 'blocked_ds.dart';


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

  void _showLoadingDialog(BuildContext context, {String message = 'Loading...'}) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (_) => AlertDialog(
        content: Row(
          children: [
            const CircularProgressIndicator(),
            const SizedBox(width: 16),
            Text(message),
          ],
        ),
      ),
    );
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
                Navigator.of(context).pop(); // Close device detail dialog
                _showLoadingDialog(context, message: "Scanning...");
                scanDevice(device['ip']);
              },
              child: const Text('Scan'),
            ),
            TextButton(
              onPressed: () async {
                Navigator.of(context).pop(); // Close device detail dialog

                // _showLoadingDialog(context, message: "Blocking..."); // <-- Commented out

                final response = await http.post(
                  Uri.parse('http://10.15.159.179:5000/block-device'),
                  headers: {'Content-Type': 'application/json'},
                  body: jsonEncode({'ip': device['ip']}),
                );

                // Navigator.of(context).pop(); // <-- Commented out (remove closing of loading dialog)

                final resBody = jsonDecode(response.body);
                showDialog(
                  context: context,
                  builder: (_) => AlertDialog(
                    title: Text(response.statusCode == 200 ? 'Blocked' : 'Error'),
                    content: Text(resBody['status'] ?? resBody['error'] ?? 'Unknown result'),
                  ),
                );
                await loadData();
              },
              child: const Text('Block'),
            ),
          ],
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title),
        actions: [
          IconButton(
            icon: const Icon(
              Icons.block,
              color: Colors.lightBlueAccent,
            ),
            tooltip: 'Blocked Devices',
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const BlockedDevicesScreen()),
              );
            },
          ),
        ],
      ),
      body: devices.isEmpty
          ? const Center(child: Text("No devices found or failed to load."))
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

      Navigator.of(context).pop(); // ✅ Close loading

      if (response.statusCode == 200) {
        final result = jsonDecode(response.body);

        if (result['hosts'] == null || result['hosts'].isEmpty) {
          Navigator.of(context, rootNavigator: true).pop();
          showDialog(
            context: context,
            builder: (_) => AlertDialog(
              title: const Text("No Device Found"),
              content: const Text("No matching device found during scan."),
            ),
          );
          return;
        }

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
            title: const Text("Scan Complete"),
            content: Text("Device ${newHost['host']} updated."),
          ),
        );
      } else {
        showDialog(
          context: context,
          builder: (_) => AlertDialog(
            title: const Text("Scan Failed"),
            content: Text("Server error: ${response.body}"),
          ),
        );
      }
    } catch (e) {
      Navigator.of(context).pop(); // ✅ Close loading on error

      showDialog(
        context: context,
        builder: (_) => AlertDialog(
          title: const Text("Error"),
          content: const Text("Could not connect to scanner server."),
        ),
      );
    } finally {
      setState(() {
        isScanning = false;
      });
    }
  }

}