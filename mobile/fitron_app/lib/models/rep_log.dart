class RepLog {
  final String id;
  final String userId;
  final String exerciseName;
  final int setNumber;
  final int repNumber;
  final double weight;
  final int reps;
  final DateTime timestamp;
  final Map<String, dynamic>? poseData;
  final double? formScore;
  final String? formFeedback;
  final double? velocity;
  final double? rangeOfMotion;
  final bool? isEgoLifting;
  final Map<String, dynamic>? fatigueIndicators;
  final String? videoUrl;
  final Map<String, dynamic>? metadata;

  RepLog({
    required this.id,
    required this.userId,
    required this.exerciseName,
    required this.setNumber,
    required this.repNumber,
    required this.weight,
    required this.reps,
    required this.timestamp,
    this.poseData,
    this.formScore,
    this.formFeedback,
    this.velocity,
    this.rangeOfMotion,
    this.isEgoLifting,
    this.fatigueIndicators,
    this.videoUrl,
    this.metadata,
  });

  factory RepLog.fromJson(Map<String, dynamic> json) {
    return RepLog(
      id: json['id'],
      userId: json['user_id'],
      exerciseName: json['exercise_name'],
      setNumber: json['set_number'],
      repNumber: json['rep_number'],
      weight: json['weight'].toDouble(),
      reps: json['reps'],
      timestamp: DateTime.parse(json['timestamp']),
      poseData: json['pose_data'],
      formScore: json['form_score']?.toDouble(),
      formFeedback: json['form_feedback'],
      velocity: json['velocity']?.toDouble(),
      rangeOfMotion: json['range_of_motion']?.toDouble(),
      isEgoLifting: json['is_ego_lifting'],
      fatigueIndicators: json['fatigue_indicators'],
      videoUrl: json['video_url'],
      metadata: json['metadata'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'exercise_name': exerciseName,
      'set_number': setNumber,
      'rep_number': repNumber,
      'weight': weight,
      'reps': reps,
      'timestamp': timestamp.toIso8601String(),
      'pose_data': poseData,
      'form_score': formScore,
      'form_feedback': formFeedback,
      'velocity': velocity,
      'range_of_motion': rangeOfMotion,
      'is_ego_lifting': isEgoLifting,
      'fatigue_indicators': fatigueIndicators,
      'video_url': videoUrl,
      'metadata': metadata,
    };
  }

  RepLog copyWith({
    String? id,
    String? userId,
    String? exerciseName,
    int? setNumber,
    int? repNumber,
    double? weight,
    int? reps,
    DateTime? timestamp,
    Map<String, dynamic>? poseData,
    double? formScore,
    String? formFeedback,
    double? velocity,
    double? rangeOfMotion,
    bool? isEgoLifting,
    Map<String, dynamic>? fatigueIndicators,
    String? videoUrl,
    Map<String, dynamic>? metadata,
  }) {
    return RepLog(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      exerciseName: exerciseName ?? this.exerciseName,
      setNumber: setNumber ?? this.setNumber,
      repNumber: repNumber ?? this.repNumber,
      weight: weight ?? this.weight,
      reps: reps ?? this.reps,
      timestamp: timestamp ?? this.timestamp,
      poseData: poseData ?? this.poseData,
      formScore: formScore ?? this.formScore,
      formFeedback: formFeedback ?? this.formFeedback,
      velocity: velocity ?? this.velocity,
      rangeOfMotion: rangeOfMotion ?? this.rangeOfMotion,
      isEgoLifting: isEgoLifting ?? this.isEgoLifting,
      fatigueIndicators: fatigueIndicators ?? this.fatigueIndicators,
      videoUrl: videoUrl ?? this.videoUrl,
      metadata: metadata ?? this.metadata,
    );
  }

  bool get isGoodForm => formScore != null && formScore! >= 0.7;
  bool get needsFormCorrection => formScore != null && formScore! < 0.7;
  bool get isDangerous => isEgoLifting == true;

  @override
  String toString() {
    return 'RepLog(id: $id, exercise: $exerciseName, set: $setNumber, rep: $repNumber, weight: $weight, formScore: $formScore)';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is RepLog && other.id == id;
  }

  @override
  int get hashCode => id.hashCode;
} 