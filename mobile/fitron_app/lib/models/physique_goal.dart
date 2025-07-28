class PhysiqueGoal {
  final String id;
  final String userId;
  final String goalName;
  final String description;
  final String? celebrityReference;
  final Map<String, dynamic>? targetMetrics;
  final Map<String, dynamic>? currentMetrics;
  final DateTime targetDate;
  final DateTime createdAt;
  final DateTime updatedAt;
  final String status; // 'active', 'completed', 'paused', 'cancelled'
  final double progress; // 0.0 to 1.0
  final List<Map<String, dynamic>>? milestones;
  final Map<String, dynamic>? trainingPlan;
  final Map<String, dynamic>? nutritionPlan;
  final List<String>? exercises;
  final Map<String, dynamic>? celebrityAnalysis;
  final Map<String, dynamic>? geneticFactors;
  final String? difficultyLevel; // 'beginner', 'intermediate', 'advanced', 'elite'

  PhysiqueGoal({
    required this.id,
    required this.userId,
    required this.goalName,
    required this.description,
    this.celebrityReference,
    this.targetMetrics,
    this.currentMetrics,
    required this.targetDate,
    required this.createdAt,
    required this.updatedAt,
    required this.status,
    required this.progress,
    this.milestones,
    this.trainingPlan,
    this.nutritionPlan,
    this.exercises,
    this.celebrityAnalysis,
    this.geneticFactors,
    this.difficultyLevel,
  });

  factory PhysiqueGoal.fromJson(Map<String, dynamic> json) {
    return PhysiqueGoal(
      id: json['id'],
      userId: json['user_id'],
      goalName: json['goal_name'],
      description: json['description'],
      celebrityReference: json['celebrity_reference'],
      targetMetrics: json['target_metrics'],
      currentMetrics: json['current_metrics'],
      targetDate: DateTime.parse(json['target_date']),
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: DateTime.parse(json['updated_at']),
      status: json['status'],
      progress: json['progress'].toDouble(),
      milestones: json['milestones'] != null 
          ? List<Map<String, dynamic>>.from(json['milestones']) 
          : null,
      trainingPlan: json['training_plan'],
      nutritionPlan: json['nutrition_plan'],
      exercises: json['exercises'] != null 
          ? List<String>.from(json['exercises']) 
          : null,
      celebrityAnalysis: json['celebrity_analysis'],
      geneticFactors: json['genetic_factors'],
      difficultyLevel: json['difficulty_level'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'goal_name': goalName,
      'description': description,
      'celebrity_reference': celebrityReference,
      'target_metrics': targetMetrics,
      'current_metrics': currentMetrics,
      'target_date': targetDate.toIso8601String(),
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
      'status': status,
      'progress': progress,
      'milestones': milestones,
      'training_plan': trainingPlan,
      'nutrition_plan': nutritionPlan,
      'exercises': exercises,
      'celebrity_analysis': celebrityAnalysis,
      'genetic_factors': geneticFactors,
      'difficulty_level': difficultyLevel,
    };
  }

  PhysiqueGoal copyWith({
    String? id,
    String? userId,
    String? goalName,
    String? description,
    String? celebrityReference,
    Map<String, dynamic>? targetMetrics,
    Map<String, dynamic>? currentMetrics,
    DateTime? targetDate,
    DateTime? createdAt,
    DateTime? updatedAt,
    String? status,
    double? progress,
    List<Map<String, dynamic>>? milestones,
    Map<String, dynamic>? trainingPlan,
    Map<String, dynamic>? nutritionPlan,
    List<String>? exercises,
    Map<String, dynamic>? celebrityAnalysis,
    Map<String, dynamic>? geneticFactors,
    String? difficultyLevel,
  }) {
    return PhysiqueGoal(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      goalName: goalName ?? this.goalName,
      description: description ?? this.description,
      celebrityReference: celebrityReference ?? this.celebrityReference,
      targetMetrics: targetMetrics ?? this.targetMetrics,
      currentMetrics: currentMetrics ?? this.currentMetrics,
      targetDate: targetDate ?? this.targetDate,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      status: status ?? this.status,
      progress: progress ?? this.progress,
      milestones: milestones ?? this.milestones,
      trainingPlan: trainingPlan ?? this.trainingPlan,
      nutritionPlan: nutritionPlan ?? this.nutritionPlan,
      exercises: exercises ?? this.exercises,
      celebrityAnalysis: celebrityAnalysis ?? this.celebrityAnalysis,
      geneticFactors: geneticFactors ?? this.geneticFactors,
      difficultyLevel: difficultyLevel ?? this.difficultyLevel,
    );
  }

  bool get isActive => status == 'active';
  bool get isCompleted => status == 'completed';
  bool get isPaused => status == 'paused';
  bool get isCancelled => status == 'cancelled';
  
  int get daysRemaining {
    final now = DateTime.now();
    return targetDate.difference(now).inDays;
  }
  
  bool get isOverdue => daysRemaining < 0;
  
  String get progressPercentage => '${(progress * 100).toStringAsFixed(1)}%';

  @override
  String toString() {
    return 'PhysiqueGoal(id: $id, name: $goalName, progress: $progressPercentage, status: $status)';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is PhysiqueGoal && other.id == id;
  }

  @override
  int get hashCode => id.hashCode;
} 