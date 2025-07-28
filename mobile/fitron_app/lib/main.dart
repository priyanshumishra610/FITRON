import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import 'package:hive_flutter/hive_flutter.dart';

import 'screens/splash_screen.dart';
import 'screens/auth/login_screen.dart';
import 'screens/auth/register_screen.dart';
import 'screens/home/home_screen.dart';
import 'screens/workout/workout_screen.dart';
import 'screens/analytics/analytics_screen.dart';
import 'screens/profile/profile_screen.dart';
import 'screens/goals/goals_screen.dart';

import 'services/auth_service.dart';
import 'services/api_service.dart';
import 'services/storage_service.dart';
import 'services/notification_service.dart';

import 'models/user.dart';
import 'models/workout_session.dart';
import 'models/physique_goal.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize Hive
  await Hive.initFlutter();
  Hive.registerAdapter(UserAdapter());
  Hive.registerAdapter(WorkoutSessionAdapter());
  Hive.registerAdapter(PhysiqueGoalAdapter());
  
  // Set preferred orientations
  await SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
    DeviceOrientation.portraitDown,
  ]);
  
  // Set system UI overlay style
  SystemChrome.setSystemUIOverlayStyle(
    const SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      statusBarIconBrightness: Brightness.dark,
      systemNavigationBarColor: Colors.white,
      systemNavigationBarIconBrightness: Brightness.dark,
    ),
  );
  
  runApp(const FITRONApp());
}

class FITRONApp extends StatelessWidget {
  const FITRONApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthService()),
        ChangeNotifierProvider(create: (_) => ApiService()),
        ChangeNotifierProvider(create: (_) => StorageService()),
        ChangeNotifierProvider(create: (_) => NotificationService()),
      ],
      child: MaterialApp.router(
        title: 'FITRON AI Fitness OS',
        debugShowCheckedModeBanner: false,
        theme: _buildTheme(),
        routerConfig: _buildRouter(),
      ),
    );
  }

  ThemeData _buildTheme() {
    return ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(
        seedColor: const Color(0xFF1E88E5),
        brightness: Brightness.light,
      ),
      fontFamily: 'Inter',
      appBarTheme: const AppBarTheme(
        elevation: 0,
        centerTitle: true,
        backgroundColor: Colors.transparent,
        foregroundColor: Colors.black,
        titleTextStyle: TextStyle(
          color: Colors.black,
          fontSize: 20,
          fontWeight: FontWeight.w600,
          fontFamily: 'Inter',
        ),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          elevation: 0,
          padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          textStyle: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w600,
            fontFamily: 'Inter',
          ),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: Colors.grey),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: Colors.grey),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: Color(0xFF1E88E5), width: 2),
        ),
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
      ),
      cardTheme: CardTheme(
        elevation: 2,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
        ),
      ),
    );
  }

  GoRouter _buildRouter() {
    return GoRouter(
      initialLocation: '/',
      routes: [
        GoRoute(
          path: '/',
          builder: (context, state) => const SplashScreen(),
        ),
        GoRoute(
          path: '/login',
          builder: (context, state) => const LoginScreen(),
        ),
        GoRoute(
          path: '/register',
          builder: (context, state) => const RegisterScreen(),
        ),
        GoRoute(
          path: '/home',
          builder: (context, state) => const HomeScreen(),
        ),
        GoRoute(
          path: '/workout',
          builder: (context, state) => const WorkoutScreen(),
        ),
        GoRoute(
          path: '/analytics',
          builder: (context, state) => const AnalyticsScreen(),
        ),
        GoRoute(
          path: '/goals',
          builder: (context, state) => const GoalsScreen(),
        ),
        GoRoute(
          path: '/profile',
          builder: (context, state) => const ProfileScreen(),
        ),
      ],
      redirect: (context, state) {
        final authService = context.read<AuthService>();
        final isLoggedIn = authService.isLoggedIn;
        
        // If user is not logged in and trying to access protected routes
        if (!isLoggedIn && state.matchedLocation != '/' && 
            state.matchedLocation != '/login' && 
            state.matchedLocation != '/register') {
          return '/login';
        }
        
        // If user is logged in and on auth screens, redirect to home
        if (isLoggedIn && (state.matchedLocation == '/login' || 
                          state.matchedLocation == '/register')) {
          return '/home';
        }
        
        return null;
      },
    );
  }
}

// Hive adapters for data models
class UserAdapter extends TypeAdapter<User> {
  @override
  final int typeId = 0;

  @override
  User read(BinaryReader reader) {
    return User(
      id: reader.readInt(),
      email: reader.readString(),
      username: reader.readString(),
      fullName: reader.readString(),
      age: reader.readInt(),
      heightCm: reader.readDouble(),
      weightKg: reader.readDouble(),
      fitnessLevel: reader.readString(),
      primaryGoal: reader.readString(),
      isProUser: reader.readBool(),
    );
  }

  @override
  void write(BinaryWriter writer, User obj) {
    writer.writeInt(obj.id);
    writer.writeString(obj.email);
    writer.writeString(obj.username);
    writer.writeString(obj.fullName);
    writer.writeInt(obj.age);
    writer.writeDouble(obj.heightCm);
    writer.writeDouble(obj.weightKg);
    writer.writeString(obj.fitnessLevel);
    writer.writeString(obj.primaryGoal);
    writer.writeBool(obj.isProUser);
  }
}

class WorkoutSessionAdapter extends TypeAdapter<WorkoutSession> {
  @override
  final int typeId = 1;

  @override
  WorkoutSession read(BinaryReader reader) {
    return WorkoutSession(
      id: reader.readString(),
      userId: reader.readInt(),
      startTime: DateTime.parse(reader.readString()),
      endTime: reader.readString().isNotEmpty 
          ? DateTime.parse(reader.readString()) 
          : null,
      exercises: List<String>.from(reader.readList()),
      totalReps: reader.readInt(),
      totalSets: reader.readInt(),
      averageFormScore: reader.readDouble(),
    );
  }

  @override
  void write(BinaryWriter writer, WorkoutSession obj) {
    writer.writeString(obj.id);
    writer.writeInt(obj.userId);
    writer.writeString(obj.startTime.toIso8601String());
    writer.writeString(obj.endTime?.toIso8601String() ?? '');
    writer.writeList(obj.exercises);
    writer.writeInt(obj.totalReps);
    writer.writeInt(obj.totalSets);
    writer.writeDouble(obj.averageFormScore);
  }
}

class PhysiqueGoalAdapter extends TypeAdapter<PhysiqueGoal> {
  @override
  final int typeId = 2;

  @override
  PhysiqueGoal read(BinaryReader reader) {
    return PhysiqueGoal(
      id: reader.readInt(),
      userId: reader.readInt(),
      goalName: reader.readString(),
      physiqueCategory: reader.readString(),
      targetCelebrity: reader.readString(),
      targetWeightKg: reader.readDouble(),
      targetBodyFatPercentage: reader.readDouble(),
      targetMuscleMassKg: reader.readDouble(),
      currentWeightKg: reader.readDouble(),
      currentBodyFatPercentage: reader.readDouble(),
      currentMuscleMassKg: reader.readDouble(),
      progressPercentage: reader.readDouble(),
      startDate: DateTime.parse(reader.readString()),
      targetDate: reader.readString().isNotEmpty 
          ? DateTime.parse(reader.readString()) 
          : null,
    );
  }

  @override
  void write(BinaryWriter writer, PhysiqueGoal obj) {
    writer.writeInt(obj.id);
    writer.writeInt(obj.userId);
    writer.writeString(obj.goalName);
    writer.writeString(obj.physiqueCategory);
    writer.writeString(obj.targetCelebrity);
    writer.writeDouble(obj.targetWeightKg);
    writer.writeDouble(obj.targetBodyFatPercentage);
    writer.writeDouble(obj.targetMuscleMassKg);
    writer.writeDouble(obj.currentWeightKg);
    writer.writeDouble(obj.currentBodyFatPercentage);
    writer.writeDouble(obj.currentMuscleMassKg);
    writer.writeDouble(obj.progressPercentage);
    writer.writeString(obj.startDate.toIso8601String());
    writer.writeString(obj.targetDate?.toIso8601String() ?? '');
  }
} 