// shared/presentation/templates/auth_template.dart
// Template: layout skeleton with slots, uses FScaffold
import 'package:flutter/widgets.dart';
import 'package:forui/forui.dart';

class AuthTemplate extends StatelessWidget {
  final Widget header;
  final Widget body;
  final Widget? footer;

  const AuthTemplate({
    super.key,
    required this.header,
    required this.body,
    this.footer,
  });

  @override
  Widget build(BuildContext context) {
    return FScaffold(
      child: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            children: [
              header,
              const SizedBox(height: 32),
              FCard(
                child: body,
              ),
              if (footer != null) ...[
                const SizedBox(height: 24),
                footer!,
              ],
            ],
          ),
        ),
      ),
    );
  }
}
