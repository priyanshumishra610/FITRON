import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../api/api_client.dart';
import '../models/user.dart';

class AuthService extends ChangeNotifier {
  final ApiClient _apiClient = ApiClient();
  User? _currentUser;
  String? _authToken;
  bool _isLoading = false;

  User? get currentUser => _currentUser;
  String? get authToken => _authToken;
  bool get isLoading => _isLoading;
  bool get isAuthenticated => _authToken != null && _currentUser != null;

  AuthService() {
    _loadStoredAuth();
  }

  Future<void> _loadStoredAuth() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('auth_token');
      final userData = prefs.getString('user_data');

      if (token != null && userData != null) {
        _authToken = token;
        _currentUser = User.fromJson(jsonDecode(userData));
        _apiClient.setAuthToken(token);
        notifyListeners();
      }
    } catch (e) {
      debugPrint('Error loading stored auth: $e');
    }
  }

  Future<void> _storeAuth(String token, User user) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('auth_token', token);
      await prefs.setString('user_data', jsonEncode(user.toJson()));
    } catch (e) {
      debugPrint('Error storing auth: $e');
    }
  }

  Future<void> _clearStoredAuth() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove('auth_token');
      await prefs.remove('user_data');
    } catch (e) {
      debugPrint('Error clearing stored auth: $e');
    }
  }

  Future<void> login(String email, String password) async {
    _setLoading(true);
    
    try {
      final response = await _apiClient.login(email, password);
      
      final token = response['access_token'];
      final user = User.fromJson(response['user']);
      
      _authToken = token;
      _currentUser = user;
      _apiClient.setAuthToken(token);
      
      await _storeAuth(token, user);
      notifyListeners();
    } finally {
      _setLoading(false);
    }
  }

  Future<void> register(String email, String password, String name) async {
    _setLoading(true);
    
    try {
      final response = await _apiClient.register(email, password, name);
      
      final token = response['access_token'];
      final user = User.fromJson(response['user']);
      
      _authToken = token;
      _currentUser = user;
      _apiClient.setAuthToken(token);
      
      await _storeAuth(token, user);
      notifyListeners();
    } finally {
      _setLoading(false);
    }
  }

  Future<void> logout() async {
    _setLoading(true);
    
    try {
      _authToken = null;
      _currentUser = null;
      _apiClient.clearAuthToken();
      
      await _clearStoredAuth();
      notifyListeners();
    } finally {
      _setLoading(false);
    }
  }

  Future<void> refreshUserProfile() async {
    if (!isAuthenticated) return;
    
    try {
      final user = await _apiClient.getUserProfile();
      _currentUser = user;
      
      // Update stored user data
      if (_authToken != null) {
        await _storeAuth(_authToken!, user);
      }
      
      notifyListeners();
    } catch (e) {
      debugPrint('Error refreshing user profile: $e');
    }
  }

  Future<void> updateProfile(Map<String, dynamic> updates) async {
    if (!isAuthenticated) return;
    
    _setLoading(true);
    
    try {
      final user = await _apiClient.updateUserProfile(updates);
      _currentUser = user;
      
      // Update stored user data
      if (_authToken != null) {
        await _storeAuth(_authToken!, user);
      }
      
      notifyListeners();
    } finally {
      _setLoading(false);
    }
  }

  Future<void> forgotPassword(String email) async {
    _setLoading(true);
    
    try {
      // Implement forgot password API call
      await Future.delayed(const Duration(seconds: 2)); // Simulate API call
    } finally {
      _setLoading(false);
    }
  }

  Future<void> resetPassword(String token, String newPassword) async {
    _setLoading(true);
    
    try {
      // Implement reset password API call
      await Future.delayed(const Duration(seconds: 2)); // Simulate API call
    } finally {
      _setLoading(false);
    }
  }

  void _setLoading(bool loading) {
    _isLoading = loading;
    notifyListeners();
  }

  // Check if token is expired
  bool get isTokenExpired {
    // Implement token expiration check
    return false;
  }

  // Auto-refresh token if needed
  Future<void> refreshTokenIfNeeded() async {
    if (isTokenExpired && isAuthenticated) {
      try {
        // Implement token refresh logic
        await Future.delayed(const Duration(seconds: 1)); // Simulate API call
      } catch (e) {
        // If refresh fails, logout user
        await logout();
      }
    }
  }
} 