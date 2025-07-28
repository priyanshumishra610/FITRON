import 'dart:convert';
import 'package:flutter/foundation.dart';
import '../api/api_client.dart';
import '../models/rep_log.dart';

class WorkoutService extends ChangeNotifier {
  final ApiClient _apiClient = ApiClient();
  
  List<RepLog> _todayReps = [];
  List<RepLog> _recentReps = [];
  Map<String, dynamic>? _currentWorkout;
  bool _isLoading = false;
  bool _isWorkoutActive = false;

  List<RepLog> get todayReps => _todayReps;
  List<RepLog> get recentReps => _recentReps;
  Map<String, dynamic>? get currentWorkout => _currentWorkout;
  bool get isLoading => _isLoading;
  bool get isWorkoutActive => _isWorkoutActive;

  // Load today's workout data
  Future<void> loadTodayWorkout() async {
    _setLoading(true);
    
    try {
      final today = DateTime.now();
      final startOfDay = DateTime(today.year, today.month, today.day);
      final endOfDay = startOfDay.add(const Duration(days: 1));
      
      final reps = await _apiClient.getRepLogs(
        startDate: startOfDay,
        endDate: endOfDay,
      );
      
      _todayReps = reps;
      notifyListeners();
    } catch (e) {
      debugPrint('Error loading today\'s workout: $e');
    } finally {
      _setLoading(false);
    }
  }

  // Load recent rep logs
  Future<void> loadRecentReps({int days = 7}) async {
    _setLoading(true);
    
    try {
      final endDate = DateTime.now();
      final startDate = endDate.subtract(Duration(days: days));
      
      final reps = await _apiClient.getRepLogs(
        startDate: startDate,
        endDate: endDate,
      );
      
      _recentReps = reps;
      notifyListeners();
    } catch (e) {
      debugPrint('Error loading recent reps: $e');
    } finally {
      _setLoading(false);
    }
  }

  // Start a new workout session
  Future<void> startWorkout(String workoutType) async {
    _setLoading(true);
    
    try {
      _currentWorkout = {
        'id': DateTime.now().millisecondsSinceEpoch.toString(),
        'type': workoutType,
        'startTime': DateTime.now().toIso8601String(),
        'exercises': [],
        'status': 'active',
      };
      
      _isWorkoutActive = true;
      notifyListeners();
    } finally {
      _setLoading(false);
    }
  }

  // End current workout session
  Future<void> endWorkout() async {
    if (!_isWorkoutActive) return;
    
    _setLoading(true);
    
    try {
      if (_currentWorkout != null) {
        _currentWorkout!['endTime'] = DateTime.now().toIso8601String();
        _currentWorkout!['status'] = 'completed';
        _currentWorkout!['duration'] = _calculateWorkoutDuration();
      }
      
      _isWorkoutActive = false;
      _currentWorkout = null;
      notifyListeners();
    } finally {
      _setLoading(false);
    }
  }

  // Log a single rep
  Future<RepLog> logRep({
    required String exerciseName,
    required int setNumber,
    required int repNumber,
    required double weight,
    required int reps,
    Map<String, dynamic>? poseData,
    double? formScore,
    String? formFeedback,
  }) async {
    _setLoading(true);
    
    try {
      final repLog = RepLog(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        userId: 'current_user_id', // This should come from auth service
        exerciseName: exerciseName,
        setNumber: setNumber,
        repNumber: repNumber,
        weight: weight,
        reps: reps,
        timestamp: DateTime.now(),
        poseData: poseData,
        formScore: formScore,
        formFeedback: formFeedback,
      );

      final savedRepLog = await _apiClient.logRep(repLog);
      
      // Add to today's reps
      _todayReps.add(savedRepLog);
      
      // Add to current workout if active
      if (_isWorkoutActive && _currentWorkout != null) {
        _currentWorkout!['exercises'].add({
          'name': exerciseName,
          'set': setNumber,
          'rep': repNumber,
          'weight': weight,
          'reps': reps,
          'formScore': formScore,
          'timestamp': DateTime.now().toIso8601String(),
        });
      }
      
      notifyListeners();
      return savedRepLog;
    } finally {
      _setLoading(false);
    }
  }

  // Analyze pose from video
  Future<Map<String, dynamic>> analyzePose(String videoPath) async {
    _setLoading(true);
    
    try {
      final result = await _apiClient.analyzePose(videoPath as dynamic);
      return result;
    } finally {
      _setLoading(false);
    }
  }

  // Get auto-regulation status
  Future<Map<String, dynamic>> getAutoRegulationStatus() async {
    try {
      return await _apiClient.getAutoRegulationStatus();
    } catch (e) {
      debugPrint('Error getting auto-regulation status: $e');
      return {
        'is_locked': false,
        'reason': null,
        'recommendations': [],
      };
    }
  }

  // Override auto-regulation
  Future<Map<String, dynamic>> overrideAutoRegulation(String reason) async {
    _setLoading(true);
    
    try {
      final result = await _apiClient.overrideAutoRegulation(reason);
      return result;
    } finally {
      _setLoading(false);
    }
  }

  // Get workout statistics
  Map<String, dynamic> getWorkoutStats() {
    if (_todayReps.isEmpty) {
      return {
        'totalReps': 0,
        'totalSets': 0,
        'totalWeight': 0.0,
        'averageFormScore': 0.0,
        'exercises': [],
        'duration': 0,
      };
    }

    final totalReps = _todayReps.fold(0, (sum, rep) => sum + rep.reps);
    final totalSets = _todayReps.map((rep) => rep.setNumber).toSet().length;
    final totalWeight = _todayReps.fold(0.0, (sum, rep) => sum + (rep.weight * rep.reps));
    
    final formScores = _todayReps.where((rep) => rep.formScore != null).map((rep) => rep.formScore!);
    final averageFormScore = formScores.isNotEmpty ? formScores.reduce((a, b) => a + b) / formScores.length : 0.0;
    
    final exercises = _todayReps.map((rep) => rep.exerciseName).toSet().toList();
    
    return {
      'totalReps': totalReps,
      'totalSets': totalSets,
      'totalWeight': totalWeight,
      'averageFormScore': averageFormScore,
      'exercises': exercises,
      'duration': _calculateWorkoutDuration(),
    };
  }

  // Get form analysis for recent reps
  List<Map<String, dynamic>> getFormAnalysis() {
    return _recentReps
        .where((rep) => rep.formScore != null)
        .map((rep) => {
              'exercise': rep.exerciseName,
              'formScore': rep.formScore,
              'feedback': rep.formFeedback,
              'timestamp': rep.timestamp,
              'isGoodForm': rep.isGoodForm,
            })
        .toList();
  }

  // Get ego-lifting alerts
  List<RepLog> getEgoLiftingAlerts() {
    return _recentReps.where((rep) => rep.isEgoLifting == true).toList();
  }

  // Get fatigue indicators
  List<RepLog> getFatigueIndicators() {
    return _recentReps.where((rep) => rep.fatigueIndicators != null).toList();
  }

  void _setLoading(bool loading) {
    _isLoading = loading;
    notifyListeners();
  }

  int _calculateWorkoutDuration() {
    if (_currentWorkout == null || _currentWorkout!['startTime'] == null) {
      return 0;
    }
    
    final startTime = DateTime.parse(_currentWorkout!['startTime']);
    final endTime = _currentWorkout!['endTime'] != null 
        ? DateTime.parse(_currentWorkout!['endTime'])
        : DateTime.now();
    
    return endTime.difference(startTime).inMinutes;
  }

  // Clear all data (for testing or logout)
  void clearData() {
    _todayReps.clear();
    _recentReps.clear();
    _currentWorkout = null;
    _isWorkoutActive = false;
    notifyListeners();
  }
} 