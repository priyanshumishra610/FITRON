class User {
  final String id;
  final String email;
  final String name;
  final String? profileImage;
  final DateTime createdAt;
  final DateTime updatedAt;
  final Map<String, dynamic>? preferences;
  final String? subscriptionTier;
  final DateTime? subscriptionExpiry;
  final Map<String, dynamic>? bodyMetrics;
  final List<String>? goals;

  User({
    required this.id,
    required this.email,
    required this.name,
    this.profileImage,
    required this.createdAt,
    required this.updatedAt,
    this.preferences,
    this.subscriptionTier,
    this.subscriptionExpiry,
    this.bodyMetrics,
    this.goals,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'],
      email: json['email'],
      name: json['name'],
      profileImage: json['profile_image'],
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: DateTime.parse(json['updated_at']),
      preferences: json['preferences'],
      subscriptionTier: json['subscription_tier'],
      subscriptionExpiry: json['subscription_expiry'] != null 
          ? DateTime.parse(json['subscription_expiry']) 
          : null,
      bodyMetrics: json['body_metrics'],
      goals: json['goals'] != null 
          ? List<String>.from(json['goals']) 
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'name': name,
      'profile_image': profileImage,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
      'preferences': preferences,
      'subscription_tier': subscriptionTier,
      'subscription_expiry': subscriptionExpiry?.toIso8601String(),
      'body_metrics': bodyMetrics,
      'goals': goals,
    };
  }

  User copyWith({
    String? id,
    String? email,
    String? name,
    String? profileImage,
    DateTime? createdAt,
    DateTime? updatedAt,
    Map<String, dynamic>? preferences,
    String? subscriptionTier,
    DateTime? subscriptionExpiry,
    Map<String, dynamic>? bodyMetrics,
    List<String>? goals,
  }) {
    return User(
      id: id ?? this.id,
      email: email ?? this.email,
      name: name ?? this.name,
      profileImage: profileImage ?? this.profileImage,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      preferences: preferences ?? this.preferences,
      subscriptionTier: subscriptionTier ?? this.subscriptionTier,
      subscriptionExpiry: subscriptionExpiry ?? this.subscriptionExpiry,
      bodyMetrics: bodyMetrics ?? this.bodyMetrics,
      goals: goals ?? this.goals,
    );
  }

  @override
  String toString() {
    return 'User(id: $id, email: $email, name: $name)';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is User && other.id == id;
  }

  @override
  int get hashCode => id.hashCode;
} 