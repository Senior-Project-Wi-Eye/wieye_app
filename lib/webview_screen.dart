import 'package:flutter/material.dart';
import 'package:webview_windows/webview_windows.dart';

class WebviewScreen extends StatefulWidget {
  final String url;
  final String title;

  const WebviewScreen({super.key, required this.url, required this.title});

  @override
  State<WebviewScreen> createState() => _WebviewScreenState();
}

class _WebviewScreenState extends State<WebviewScreen> {
  final _controller = WebviewController();
  bool _isInitialized = false;

  @override
  void initState() {
    super.initState();
    _initializeWebView();
  }

  Future<void> _initializeWebView() async {
    await _controller.initialize();
    await _controller.loadUrl(widget.url);

    setState(() {
      _isInitialized = true;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(widget.title)),
      body: _isInitialized
          ? Webview(_controller)
          : const Center(child: CircularProgressIndicator()),
    );
  }
}
