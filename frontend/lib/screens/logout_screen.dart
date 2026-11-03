import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'login_screen.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class LogoutScreen extends StatefulWidget {
  const LogoutScreen({super.key});

  @override
  State<LogoutScreen> createState() => _LogoutScreenState();
}

class _LogoutScreenState extends State<LogoutScreen>{
  final FlutterSecureStorage _storage = const FlutterSecureStorage();

  static const String baseUrl ='http://127.0.0.1:5000';

  bool _loggingOut =false;

  Future<void> logout() async {
    setState((){
      _loggingOut = true;
    });

    try{
      final token = await _storage.read(key: 'token');

      if(token != null){
        await http.post(
          Uri.parse('$baseUrl/logout'),
          headers: {
            'Authorization': 'Bearer $token',
            'Content-Type': 'application/json',
          },
        );
      }
    }
    catch(e){
      debugPrint('Logout request error: $e');
    }finally{
      await _storage.delete(key: 'token');
      await _storage.delete(key: 'userID');
    }
    if (!mounted) return;
    
    Navigator.pushAndRemoveUntil(
      context,
      MaterialPageRoute(builder: (context)=> LoginScreen(
        onLoginSuccess: () {},
      ),
        
      ), (route)=> false,
    );
    
  }

@override
Widget build(BuildContext context) {
  return Scaffold(
    appBar: AppBar(
      title: const Text('Logout'),
      ),
      body: Center(
        child: ElevatedButton(
          onPressed: _loggingOut? null: logout,
          child: Text(
            _loggingOut ? 'Logging out...': 'Logout',
        ),
      ),
    ),
  );
  }
}