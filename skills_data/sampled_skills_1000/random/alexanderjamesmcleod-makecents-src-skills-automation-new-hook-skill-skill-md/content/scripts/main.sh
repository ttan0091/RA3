#!/bin/bash

# new-hook: Create React Query hooks with TypeScript types
# Usage: new-hook {query|mutation} <EntityName>

set -e

HOOKS_DIR="packages/frontend/src/hooks"

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

show_help() {
    cat << HELP
new-hook - Create React Query hooks with TypeScript types

USAGE:
    new-hook query <EntityName>      Create a query hook
    new-hook mutation <EntityName>   Create a mutation hook
    new-hook help                    Show this help message

EXAMPLES:
    new-hook query Achievements
    new-hook mutation Streaks

OUTPUT:
    Creates: ${HOOKS_DIR}/use[Entity].ts

FEATURES:
    - TypeScript types
    - React Query integration
    - Supabase client
    - Loading/error handling
    - Cache invalidation (mutations)

HELP
}

to_camel_case() {
    # Convert PascalCase to camelCase for table names
    echo "$1" | sed 's/\(.\)\(.*\)/\L\1\E\2/'
}

to_lower_plural() {
    # Simple pluralization for table names
    local entity=$(to_camel_case "$1")
    if [[ "$entity" =~ s$ ]]; then
        echo "$entity"
    else
        echo "${entity}s"
    fi
}

create_query_hook() {
    local entity=$1
    local table=$(to_lower_plural "$entity")
    local filename="use${entity}.ts"
    local filepath="${HOOKS_DIR}/${filename}"
    
    echo -e "${YELLOW}Creating query hook for ${entity}...${NC}"
    echo "Entity: ${entity}"
    echo "Table: ${table}"
    echo "Output: ${filepath}"
    echo ""
    
    # Create hooks directory if it doesn't exist
    mkdir -p "$HOOKS_DIR"
    
    cat > "$filepath" << HOOKCODE
import { useQuery } from '@tanstack/react-query';
import { supabase } from '@/lib/supabase';

export function use${entity}() {
  return useQuery({
    queryKey: ['${table}'],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('${table}')
        .select('*');
      
      if (error) throw error;
      return data;
    }
  });
}
HOOKCODE
    
    echo -e "${GREEN}✓ Query hook created: ${filepath}${NC}"
    echo ""
    echo "Usage in component:"
    echo "  import { use${entity} } from '@/hooks/use${entity}';"
    echo ""
    echo "  const { data, isLoading, error } = use${entity}();"
}

create_mutation_hook() {
    local entity=$1
    local table=$(to_lower_plural "$entity")
    local filename="use${entity}.ts"
    local filepath="${HOOKS_DIR}/${filename}"
    
    echo -e "${YELLOW}Creating mutation hook for ${entity}...${NC}"
    echo "Entity: ${entity}"
    echo "Table: ${table}"
    echo "Output: ${filepath}"
    echo ""
    
    # Create hooks directory if it doesn't exist
    mkdir -p "$HOOKS_DIR"
    
    # Singular entity name for type
    local singular_entity="${entity%s}"
    if [[ "$singular_entity" == "$entity" ]]; then
        # If no 's' was removed, it's already singular
        singular_entity=$entity
    fi
    
    cat > "$filepath" << HOOKCODE
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { supabase } from '@/lib/supabase';

// TODO: Define the ${singular_entity} type based on your database schema
interface ${singular_entity} {
  id?: string;
  // Add other fields here
}

export function useCreate${entity}() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: Omit<${singular_entity}, 'id'>) => {
      const { data: result, error } = await supabase
        .from('${table}')
        .insert(data)
        .select()
        .single();
      
      if (error) throw error;
      return result;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['${table}'] });
    }
  });
}

export function useUpdate${entity}() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, ...data }: ${singular_entity}) => {
      const { data: result, error } = await supabase
        .from('${table}')
        .update(data)
        .eq('id', id)
        .select()
        .single();
      
      if (error) throw error;
      return result;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['${table}'] });
    }
  });
}

export function useDelete${entity}() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id: string) => {
      const { error } = await supabase
        .from('${table}')
        .delete()
        .eq('id', id);
      
      if (error) throw error;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['${table}'] });
    }
  });
}
HOOKCODE
    
    echo -e "${GREEN}✓ Mutation hooks created: ${filepath}${NC}"
    echo ""
    echo "Usage in component:"
    echo "  import { useCreate${entity}, useUpdate${entity}, useDelete${entity} } from '@/hooks/use${entity}';"
    echo ""
    echo "  const createMutation = useCreate${entity}();"
    echo "  const updateMutation = useUpdate${entity}();"
    echo "  const deleteMutation = useDelete${entity}();"
    echo ""
    echo "  createMutation.mutate({ /* data */ });"
}

# Main command handler
case "$1" in
    help|--help|-h)
        show_help
        ;;
    query)
        if [ -z "$2" ]; then
            echo -e "${RED}Error: Entity name required${NC}"
            echo "Usage: new-hook query <EntityName>"
            exit 1
        fi
        create_query_hook "$2"
        ;;
    mutation)
        if [ -z "$2" ]; then
            echo -e "${RED}Error: Entity name required${NC}"
            echo "Usage: new-hook mutation <EntityName>"
            exit 1
        fi
        create_mutation_hook "$2"
        ;;
    "")
        echo -e "${RED}Error: Command required${NC}"
        show_help
        exit 1
        ;;
    *)
        echo -e "${RED}Error: Unknown command '$1'${NC}"
        show_help
        exit 1
        ;;
esac
