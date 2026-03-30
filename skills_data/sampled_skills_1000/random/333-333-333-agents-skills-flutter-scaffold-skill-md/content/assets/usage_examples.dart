// Example: Using spacing tokens
import 'package:flutter/widgets.dart';
import 'package:bastet/app/theme/tokens.dart';

class ExampleCard extends StatelessWidget {
  const ExampleCard({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      // Page-level padding
      padding: const EdgeInsets.all(AppSpacing.xxl),
      child: Column(
        children: [
          // Large gap between sections
          const SizedBox(height: AppSpacing.lg),

          // Card with standard border radius
          Container(
            padding: const EdgeInsets.all(AppSpacing.lg),
            decoration: BoxDecoration(borderRadius: AppRadii.borderMd),
            child: const Text('Card content'),
          ),

          // Small gap between related elements
          const SizedBox(height: AppSpacing.sm),

          // Button with touch target size
          GestureDetector(
            child: Container(
              height: AppSizes.buttonHeight,
              width: double.infinity,
              decoration: BoxDecoration(borderRadius: AppRadii.borderSm),
              child: Center(child: Icon(Icons.add, size: AppSizes.iconMd)),
            ),
          ),
        ],
      ),
    );
  }
}

// Example: Bottom sheet with top radius
class ExampleSheet extends StatelessWidget {
  const ExampleSheet({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: const BoxDecoration(borderRadius: AppRadii.borderTopXl),
      padding: const EdgeInsets.fromLTRB(
        AppSpacing.xxl,
        AppSpacing.lg,
        AppSpacing.xxl,
        AppSpacing.xxl,
      ),
      child: const Text('Sheet content'),
    );
  }
}

// Example: Icon button with touch target
class ExampleIconButton extends StatelessWidget {
  const ExampleIconButton({super.key});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      child: Container(
        width: AppSizes.touchTarget,
        height: AppSizes.touchTarget,
        decoration: BoxDecoration(borderRadius: AppRadii.borderSm),
        child: Center(child: Icon(Icons.star, size: AppSizes.iconMd)),
      ),
    );
  }
}
