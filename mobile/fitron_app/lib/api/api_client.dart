import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:dio/dio.dart';
import '../models/user.dart';
import '../models/rep_log.dart';
import '../models/physique_goal.dart';

class ApiClient {
  static const String baseUrl = 'http://localhost:8000';
  static const String apiVersion = '/api/v1';
  
  late Dio _dio;
  String? _authToken;

  ApiClient() {
    _dio = Dio(BaseOptions(
      baseUrl: '$baseUrl$apiVersion',
      connectTimeout: const Duration(seconds: 30),
      receiveTimeout: const Duration(seconds: 30),
    ));
    
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) {
        if (_authToken != null) {
          options.headers['Authorization'] = 'Bearer $_authToken';
        }
        handler.next(options);
      },
      onError: (error, handler) {
        print('API Error: ${error.message}');
        handler.next(error);
      },
    ));
  }

  void setAuthToken(String token) {
    _authToken = token;
  }

  void clearAuthToken() {
    _authToken = null;
  }

  // Authentication
  Future<Map<String, dynamic>> login(String email, String password) async {
    try {
      final response = await _dio.post('/auth/login', data: {
        'email': email,
        'password': password,
      });
      return response.data;
    } catch (e) {
      throw Exception('Login failed: $e');
    }
  }

  Future<Map<String, dynamic>> register(String email, String password, String name) async {
    try {
      final response = await _dio.post('/auth/register', data: {
        'email': email,
        'password': password,
        'name': name,
      });
      return response.data;
    } catch (e) {
      throw Exception('Registration failed: $e');
    }
  }

  // User Profile
  Future<User> getUserProfile() async {
    try {
      final response = await _dio.get('/auth/profile');
      return User.fromJson(response.data);
    } catch (e) {
      throw Exception('Failed to get user profile: $e');
    }
  }

  Future<User> updateUserProfile(Map<String, dynamic> updates) async {
    try {
      final response = await _dio.put('/auth/profile', data: updates);
      return User.fromJson(response.data);
    } catch (e) {
      throw Exception('Failed to update profile: $e');
    }
  }

  // Rep Tracking
  Future<RepLog> logRep(RepLog repLog) async {
    try {
      final response = await _dio.post('/rep-tracking/log', data: repLog.toJson());
      return RepLog.fromJson(response.data);
    } catch (e) {
      throw Exception('Failed to log rep: $e');
    }
  }

  Future<List<RepLog>> getRepLogs({DateTime? startDate, DateTime? endDate}) async {
    try {
      final queryParams = <String, dynamic>{};
      if (startDate != null) queryParams['start_date'] = startDate.toIso8601String();
      if (endDate != null) queryParams['end_date'] = endDate.toIso8601String();
      
      final response = await _dio.get('/rep-tracking/logs', queryParameters: queryParams);
      return (response.data as List).map((json) => RepLog.fromJson(json)).toList();
    } catch (e) {
      throw Exception('Failed to get rep logs: $e');
    }
  }

  // Pose Analysis
  Future<Map<String, dynamic>> analyzePose(File videoFile) async {
    try {
      final formData = FormData.fromMap({
        'video': await MultipartFile.fromFile(videoFile.path),
      });
      
      final response = await _dio.post('/rep-tracking/analyze-pose', data: formData);
      return response.data;
    } catch (e) {
      throw Exception('Failed to analyze pose: $e');
    }
  }

  // Auto Regulation
  Future<Map<String, dynamic>> getAutoRegulationStatus() async {
    try {
      final response = await _dio.get('/auto-regulation/status');
      return response.data;
    } catch (e) {
      throw Exception('Failed to get auto-regulation status: $e');
    }
  }

  Future<Map<String, dynamic>> overrideAutoRegulation(String reason) async {
    try {
      final response = await _dio.post('/auto-regulation/override', data: {
        'reason': reason,
      });
      return response.data;
    } catch (e) {
      throw Exception('Failed to override auto-regulation: $e');
    }
  }

  // Physique Goals
  Future<PhysiqueGoal> createPhysiqueGoal(PhysiqueGoal goal) async {
    try {
      final response = await _dio.post('/physique-goals/create', data: goal.toJson());
      return PhysiqueGoal.fromJson(response.data);
    } catch (e) {
      throw Exception('Failed to create physique goal: $e');
    }
  }

  Future<List<PhysiqueGoal>> getPhysiqueGoals() async {
    try {
      final response = await _dio.get('/physique-goals/list');
      return (response.data as List).map((json) => PhysiqueGoal.fromJson(json)).toList();
    } catch (e) {
      throw Exception('Failed to get physique goals: $e');
    }
  }

  Future<Map<String, dynamic>> analyzeCelebrityPhysique(String celebrityName) async {
    try {
      final response = await _dio.post('/physique-goals/analyze-celebrity', data: {
        'celebrity_name': celebrityName,
      });
      return response.data;
    } catch (e) {
      throw Exception('Failed to analyze celebrity physique: $e');
    }
  }

  // Real-time Communication
  Future<void> connectWebSocket() async {
    // WebSocket implementation for real-time updates
    // This would connect to the backend's WebSocket endpoint
  }

  void disconnectWebSocket() {
    // Disconnect WebSocket connection
  }
} 