import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;

class BlockedDevicesScreen extends StatefulWidget {
  const BlockedDevicesScreen({super.key});

  @override
  State<BlockedDevicesScreen> createState() => _BlockedDevicesScreenState();
}

class _BlockedDevicesScreenState extends State<BlockedDevicesScreen> {
  List<Map<String, dynamic>> blockedDevices = [];

  @override
  void initState() {
    super.initState();
    loadBlockedDevices();
  }

  Future<void> loadBlockedDevices() async {
    final response = await http.get(Uri.parse('http://10.15.159.179:5000/get-blocked-devices'));

    if (response.statusCode == 200) {
      final Map<String, dynamic> jsonData = json.decode(response.body);
      final devices = jsonData.entries.map((entry) {
        final device = Map<String, dynamic>.from(entry.value);
        return {
          'index': entry.key,
          'mac': device['mac_address'],
          'status': device['status'],
        };
      }).toList();

      setState(() {
        blockedDevices = devices;
      });
    } else {
      print("Failed to load blocked devices");
    }
  }

  Future<void> unblockDevice(String mac) async {
    final response = await http.post(
      Uri.parse('http://10.15.159.179:5000/unblock-device'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'mac': mac}),
    );

    if (response.statusCode == 200) {
      setState(() {
        blockedDevices.removeWhere((d) => d['mac'] == mac);
      });

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Unblocked $mac")),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Failed to unblock $mac")),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Blocked Devices")),
      body: blockedDevices.isEmpty
          ? const Center(child: Text("No blocked devices"))
          : ListView.builder(
        itemCount: blockedDevices.length,
        itemBuilder: (context, index) {
          final device = blockedDevices[index];
          return Card(
            margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            child: ListTile(
              leading: const Icon(Icons.block, color: Colors.orange),
              title: Text("MAC: ${device['mac']}"),
              subtitle: Text("Status: ${device['status']}"),
              trailing: TextButton(
                onPressed: () => unblockDevice(device['mac']),
                child: const Text("Unblock", style: TextStyle(color: Colors.blue)),
              ),
            ),
          );
        },
      ),
    );
  }
}
