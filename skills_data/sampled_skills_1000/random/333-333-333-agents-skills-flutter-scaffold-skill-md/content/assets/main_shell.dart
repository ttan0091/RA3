// Shell widget using Forui's FScaffold + FBottomNavigationBar
import 'package:flutter/widgets.dart';
import 'package:forui/forui.dart';
import 'package:go_router/go_router.dart';

class MainShell extends StatelessWidget {
  final StatefulNavigationShell navigationShell;

  const MainShell({super.key, required this.navigationShell});

  @override
  Widget build(BuildContext context) {
    return FScaffold(
      footer: FBottomNavigationBar(
        index: navigationShell.currentIndex,
        onChange: (index) => navigationShell.goBranch(
          index,
          initialLocation: index == navigationShell.currentIndex,
        ),
        children: [
          FBottomNavigationBarItem(
            icon: const Icon(FIcons.home),
            label: const Text('Home'),
          ),
          FBottomNavigationBarItem(
            icon: const Icon(FIcons.calendarDays),
            label: const Text('Bookings'),
          ),
          FBottomNavigationBarItem(
            icon: const Icon(FIcons.userRound),
            label: const Text('Profile'),
          ),
        ],
      ),
      child: navigationShell,
    );
  }
}
