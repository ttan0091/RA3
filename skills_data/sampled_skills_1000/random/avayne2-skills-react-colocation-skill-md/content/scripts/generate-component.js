#!/usr/bin/env node

/**
 * React Colocation Component Generator
 * 
 * Usage:
 *   node scripts/generate-component.js ComponentName [options]
 * 
 * Options:
 *   --feature <name>  Create inside a feature folder
 *   --with-context    Include context folder
 *   --with-hooks      Include hooks folder
 *   --with-api        Include api folder (for features)
 *   --native          Use React Native styles
 *   --full            Include all optional folders
 */

const fs = require('fs');
const path = require('path');

// Parse arguments
const args = process.argv.slice(2);
const componentName = args[0];

if (!componentName) {
  console.error('Usage: node generate-component.js ComponentName [options]');
  process.exit(1);
}

const options = {
  feature: args.includes('--feature') ? args[args.indexOf('--feature') + 1] : null,
  withContext: args.includes('--with-context') || args.includes('--full'),
  withHooks: args.includes('--with-hooks') || args.includes('--full'),
  withApi: args.includes('--with-api') || args.includes('--full'),
  native: args.includes('--native'),
  full: args.includes('--full'),
};

// Determine base path
const basePath = options.feature
  ? path.join('src', 'features', options.feature, 'components', componentName)
  : path.join('src', 'components', componentName);

// Helper to create directory
const createDir = (dir) => {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
    console.log(`📁 Created: ${dir}`);
  }
};

// Helper to write file
const writeFile = (filePath, content) => {
  fs.writeFileSync(filePath, content);
  console.log(`📄 Created: ${filePath}`);
};

// Convert PascalCase to kebab-case
const toKebabCase = (str) => 
  str.replace(/([a-z])([A-Z])/g, '$1-$2').toLowerCase();

// Convert PascalCase to camelCase
const toCamelCase = (str) => 
  str.charAt(0).toLowerCase() + str.slice(1);

const kebabName = toKebabCase(componentName);
const camelName = toCamelCase(componentName);

// Templates
const templates = {
  component: options.native
    ? `import React from 'react';
import { View, Text, Pressable } from 'react-native';
import { styles } from './${componentName}.styles';
import type { ${componentName}Props } from './types/${kebabName}.types';

export const ${componentName} = ({ children, ...props }: ${componentName}Props) => {
  return (
    <View style={styles.container}>
      <Text>{children}</Text>
    </View>
  );
};
`
    : `import React from 'react';
import styles from './${componentName}.module.css';
import type { ${componentName}Props } from './types/${kebabName}.types';

export const ${componentName} = ({ children, ...props }: ${componentName}Props) => {
  return (
    <div className={styles.container}>
      {children}
    </div>
  );
};
`,

  styles: options.native
    ? `import { StyleSheet } from 'react-native';

export const styles = StyleSheet.create({
  container: {
    // Add your styles here
  },
});
`
    : `.container {
  /* Add your styles here */
}
`,

  types: `import { ReactNode } from 'react';

export interface ${componentName}Props {
  children?: ReactNode;
  // Add your props here
}
`,

  index: `export { ${componentName} } from './${componentName}';
export type { ${componentName}Props } from './types/${kebabName}.types';
`,

  test: `import React from 'react';
import { render, screen } from '@testing-library/react${options.native ? '-native' : ''}';
import { ${componentName} } from './${componentName}';

describe('${componentName}', () => {
  it('renders correctly', () => {
    render(<${componentName}>Test</${componentName}>);
    expect(screen.getByText('Test')).toBeTruthy();
  });
});
`,

  context: `import { createContext, useContext, useState, ReactNode } from 'react';

interface ${componentName}ContextType {
  // Add your context state here
}

const ${componentName}Context = createContext<${componentName}ContextType | null>(null);

export const use${componentName}Context = () => {
  const context = useContext(${componentName}Context);
  if (!context) {
    throw new Error('use${componentName}Context must be used within ${componentName}Provider');
  }
  return context;
};

interface ${componentName}ProviderProps {
  children: ReactNode;
}

export const ${componentName}Provider = ({ children }: ${componentName}ProviderProps) => {
  // Add your state here
  const value = {};

  return (
    <${componentName}Context.Provider value={value}>
      {children}
    </${componentName}Context.Provider>
  );
};
`,

  hook: `import { useState, useCallback } from 'react';

export const use${componentName} = () => {
  // Add your hook logic here
  
  return {
    // Return your hook values
  };
};
`,

  api: `// API functions for ${componentName}

export const fetch${componentName} = async (id: string) => {
  // Implement your API call
  const response = await fetch(\`/api/${kebabName}/\${id}\`);
  return response.json();
};

export const create${componentName} = async (data: unknown) => {
  // Implement your API call
  const response = await fetch('/api/${kebabName}', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return response.json();
};
`,
};

// Create folder structure
console.log(`\n🚀 Generating ${componentName} component...\n`);

createDir(basePath);
createDir(path.join(basePath, 'types'));

// Always create these files
writeFile(
  path.join(basePath, `${componentName}.tsx`),
  templates.component
);

writeFile(
  path.join(basePath, options.native ? `${componentName}.styles.ts` : `${componentName}.module.css`),
  templates.styles
);

writeFile(
  path.join(basePath, 'types', `${kebabName}.types.ts`),
  templates.types
);

writeFile(
  path.join(basePath, 'index.ts'),
  templates.index
);

writeFile(
  path.join(basePath, `${componentName}.test.tsx`),
  templates.test
);

// Optional folders
if (options.withContext) {
  createDir(path.join(basePath, 'context'));
  writeFile(
    path.join(basePath, 'context', `${componentName}Context.tsx`),
    templates.context
  );
  
  // Update index to export context
  const indexContent = fs.readFileSync(path.join(basePath, 'index.ts'), 'utf8');
  const newIndexContent = indexContent + `export { ${componentName}Provider, use${componentName}Context } from './context/${componentName}Context';\n`;
  writeFile(path.join(basePath, 'index.ts'), newIndexContent);
}

if (options.withHooks) {
  createDir(path.join(basePath, 'hooks'));
  writeFile(
    path.join(basePath, 'hooks', `use${componentName}.ts`),
    templates.hook
  );
  
  // Update index to export hook
  const indexContent = fs.readFileSync(path.join(basePath, 'index.ts'), 'utf8');
  const newIndexContent = indexContent + `export { use${componentName} } from './hooks/use${componentName}';\n`;
  writeFile(path.join(basePath, 'index.ts'), newIndexContent);
}

if (options.withApi) {
  createDir(path.join(basePath, 'api'));
  writeFile(
    path.join(basePath, 'api', `${kebabName}.api.ts`),
    templates.api
  );
}

// Create empty components folder for subcomponents
createDir(path.join(basePath, 'components'));
writeFile(
  path.join(basePath, 'components', '.gitkeep'),
  '# Add subcomponents here\n'
);

console.log(`\n✅ ${componentName} component generated successfully!`);
console.log(`📍 Location: ${basePath}\n`);

// Print structure
console.log('Generated structure:');
console.log(`${componentName}/`);
console.log(`├── components/`);
if (options.withContext) console.log(`├── context/`);
if (options.withHooks) console.log(`├── hooks/`);
if (options.withApi) console.log(`├── api/`);
console.log(`├── types/`);
console.log(`├── ${componentName}.tsx`);
console.log(`├── ${componentName}.${options.native ? 'styles.ts' : 'module.css'}`);
console.log(`├── ${componentName}.test.tsx`);
console.log(`└── index.ts`);
