import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/auth_service.dart';
import '../services/workout_service.dart';
import '../widgets/workout_card.dart';
import '../widgets/stats_card.dart';
import '../widgets/ai_coach_widget.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _selectedIndex = 0;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadUserData();
  }

  Future<void> _loadUserData() async {
    try {
      final workoutService = context.read<WorkoutService>();
      await workoutService.loadTodayWorkout();
      setState(() => _isLoading = false);
    } catch (e) {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'FITRON',
          style: TextStyle(
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
        backgroundColor: const Color(0xFF1E3A8A),
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.notifications, color: Colors.white),
            onPressed: () {
              Navigator.of(context).pushNamed('/notifications');
            },
          ),
          IconButton(
            icon: const Icon(Icons.person, color: Colors.white),
            onPressed: () {
              Navigator.of(context).pushNamed('/profile');
            },
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : IndexedStack(
              index: _selectedIndex,
              children: const [
                _DashboardTab(),
                _WorkoutTab(),
                _GoalsTab(),
                _AnalyticsTab(),
              ],
            ),
      bottomNavigationBar: BottomNavigationBar(
        type: BottomNavigationBarType.fixed,
        currentIndex: _selectedIndex,
        onTap: (index) => setState(() => _selectedIndex = index),
        selectedItemColor: const Color(0xFF1E3A8A),
        unselectedItemColor: Colors.grey,
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.dashboard),
            label: 'Dashboard',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.fitness_center),
            label: 'Workout',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.flag),
            label: 'Goals',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.analytics),
            label: 'Analytics',
          ),
        ],
      ),
      floatingActionButton: _selectedIndex == 1
          ? FloatingActionButton.extended(
              onPressed: () {
                Navigator.of(context).pushNamed('/start-workout');
              },
              backgroundColor: const Color(0xFF1E3A8A),
              icon: const Icon(Icons.play_arrow, color: Colors.white),
              label: const Text(
                'Start Workout',
                style: TextStyle(color: Colors.white),
              ),
            )
          : null,
    );
  }
}

class _DashboardTab extends StatelessWidget {
  const _DashboardTab();

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Welcome Section
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [Color(0xFF1E3A8A), Color(0xFF3B82F6)],
              ),
              borderRadius: BorderRadius.circular(16),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Welcome back!',
                  style: TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                const SizedBox(height: 8),
                const Text(
                  'Ready to crush your fitness goals?',
                  style: TextStyle(
                    fontSize: 16,
                    color: Colors.white70,
                  ),
                ),
                const SizedBox(height: 16),
                ElevatedButton.icon(
                  onPressed: () {
                    Navigator.of(context).pushNamed('/start-workout');
                  },
                  icon: const Icon(Icons.play_arrow),
                  label: const Text('Start Today\'s Workout'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.white,
                    foregroundColor: const Color(0xFF1E3A8A),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),

          // Stats Cards
          const Text(
            'Today\'s Progress',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),
          const Row(
            children: [
              Expanded(child: StatsCard(title: 'Workouts', value: '3', icon: Icons.fitness_center)),
              SizedBox(width: 16),
              Expanded(child: StatsCard(title: 'Reps', value: '156', icon: Icons.repeat)),
            ],
          ),
          const SizedBox(height: 16),
          const Row(
            children: [
              Expanded(child: StatsCard(title: 'Calories', value: '1,240', icon: Icons.local_fire_department)),
              SizedBox(width: 16),
              Expanded(child: StatsCard(title: 'Form Score', value: '92%', icon: Icons.trending_up)),
            ],
          ),
          const SizedBox(height: 24),

          // AI Coach Widget
          const AiCoachWidget(),
          const SizedBox(height: 24),

          // Recent Workouts
          const Text(
            'Recent Workouts',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),
          const WorkoutCard(
            title: 'Upper Body Strength',
            date: 'Today',
            duration: '45 min',
            exercises: ['Bench Press', 'Pull-ups', 'Overhead Press'],
            formScore: 0.92,
          ),
          const SizedBox(height: 12),
          const WorkoutCard(
            title: 'Lower Body Power',
            date: 'Yesterday',
            duration: '50 min',
            exercises: ['Squats', 'Deadlifts', 'Lunges'],
            formScore: 0.88,
          ),
        ],
      ),
    );
  }
}

class _WorkoutTab extends StatelessWidget {
  const _WorkoutTab();

  @override
  Widget build(BuildContext context) {
    return const Center(
      child: Text(
        'Workout Tab - Coming Soon',
        style: TextStyle(fontSize: 18),
      ),
    );
  }
}

class _GoalsTab extends StatelessWidget {
  const _GoalsTab();

  @override
  Widget build(BuildContext context) {
    return const Center(
      child: Text(
        'Goals Tab - Coming Soon',
        style: TextStyle(fontSize: 18),
      ),
    );
  }
}

class _AnalyticsTab extends StatelessWidget {
  const _AnalyticsTab();

  @override
  Widget build(BuildContext context) {
    return const Center(
      child: Text(
        'Analytics Tab - Coming Soon',
        style: TextStyle(fontSize: 18),
      ),
    );
  }
} 