// app/app.dart
// App entry point: MaterialApp + FAnimatedTheme + GoRouter + Riverpod
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:forui/forui.dart';

class BastetApp extends ConsumerWidget {
  const BastetApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(routerProvider);

    // Forui theme — generated via `dart run forui init`
    // Customized with Catppuccin colors (see corporate-colors skill)
    final theme = FThemes.zinc.light; // Replace with custom Catppuccin theme

    return MaterialApp.router(
      routerConfig: router,
      title: 'Bastet',
      // Forui theme wraps the widget tree
      builder: (_, child) => FAnimatedTheme(
        data: theme,
        child: child!,
      ),
      // Approximate Material theme for compatibility with 3rd party widgets
      theme: theme.toApproximateMaterialTheme(),
      supportedLocales: FLocalizations.supportedLocales,
      localizationsDelegates: FLocalizations.localizationsDelegates,
    );
  }
}
