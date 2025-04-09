import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'home_screen.dart';
import 'current_user.dart';
// IneedaPaswword24
class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  _LoginScreenState createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();
  bool _isLoading = false;

  Future<String?> fetchUserEmail(String accessToken) async {
    final res = await http.get(
      Uri.parse('https://dev-63654183.okta.com/oauth2/default/v1/userinfo'),
      headers: {'Authorization': 'Bearer $accessToken'},
    );

    if (res.statusCode == 200) {
      final userInfo = json.decode(res.body);
      return userInfo['email'];
    }

    return null;
  }

  Future<void> _login() async {
    setState(() {
      _isLoading = true;
    });

    // Okta URL for Token request (OAuth 2.0 Token URL)
    final url = "https://dev-63654183.okta.com/oauth2/default/v1/token";
    final clientId = "0oann28vweKfjkcbH5d7";  // Okta Client ID
    final redirectUri = "com.okta.dev-63654183:/callback";  // redirect URI

    final response = await http.post(
      Uri.parse(url),
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: {
        "grant_type": "password",
        "username": _emailController.text,
        "password": _passwordController.text,
        "client_id": clientId,
        "redirect_uri": redirectUri,
        "scope": "openid profile email",
      },
    );

    setState(() {
      _isLoading = false;
    });

    print("Response status: ${response.statusCode}");
    print("Response body: ${response.body}");

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      // Check if the access token is present
      if (data['access_token'] != null) {
        print("Access Token: ${data['access_token']}");

        final email = await fetchUserEmail(data['access_token']);
        if (email != null) {
          currentUserEmail = email;
          print("Logged in as: $currentUserEmail");
        }

        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (context) => HomeScreen(title: "Home")),
        );

      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text("No access token found")),
        );
      }
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Failed Login. Please try again.")),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("Login with Okta")),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            TextField(
              controller: _emailController,
              decoration: InputDecoration(labelText: "Email"),
              keyboardType: TextInputType.emailAddress,
            ),
            TextField(
              controller: _passwordController,
              decoration: InputDecoration(labelText: "Password"),
              obscureText: true,
            ),
            SizedBox(height: 20),
            _isLoading
                ? CircularProgressIndicator()
                : ElevatedButton(
              onPressed: _login,
              child: Text("Login"),
            ),
          ],
        ),
      ),
    );
  }
}
