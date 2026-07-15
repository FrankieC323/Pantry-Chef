// Mirrors backend/app/*/schemas.py -- keep in sync manually since this is
// a small project without codegen. If the schemas grow significantly,
// consider generating these from the FastAPI OpenAPI spec instead.

export type Unit =
  | "g"
  | "kg"
  | "ml"
  | "l"
  | "tsp"
  | "tbsp"
  | "cup"
  | "fl_oz"
  | "oz"
  | "lb"
  | "piece"
  | "pinch";

export type IngredientCategory =
  | "produce"
  | "dairy"
  | "meat_seafood"
  | "grain_starch"
  | "spice_condiment"
  | "canned_jarred"
  | "frozen"
  | "baking"
  | "beverage"
  | "other";

export interface PantryItem {
  id: string;
  name: string;
  quantity: number;
  unit: Unit;
  category: IngredientCategory;
  expiration_date: string | null; // ISO date string
  added_at: string;
  updated_at: string;
  days_until_expiration: number | null;
}

export interface PantryItemCreate {
  name: string;
  quantity: number;
  unit: Unit;
  category: IngredientCategory;
  expiration_date: string | null;
}

export type RecipeSource = "spoonacular" | "scraped" | "generated";

export interface RecipeIngredient {
  id: string;
  name: string;
  raw_text: string;
  quantity: number | null;
  unit: string | null;
}

export interface Recipe {
  id: string;
  title: string;
  source: RecipeSource;
  source_url: string | null;
  instructions: string;
  servings: number;
  ready_in_minutes: number | null;
  image_url: string | null;
  cached_at: string;
  ingredients: RecipeIngredient[];
}

export interface RankedMatch {
  recipe_id: string | null;
  title: string;
  match_score: number;
  have_ingredients: string[];
  missing_ingredients: string[];
  substitution_notes: string;
  uses_expiring_items: boolean;
  reasoning: string;
  recipe: Recipe | null;
}

export interface GeneratedRecipe {
  id: string | null;
  title: string;
  servings: number;
  ingredients: { name: string; raw_text: string; quantity: number | null; unit: string | null }[];
  instructions: string;
}

export interface MatcherResponse {
  ranked_matches: RankedMatch[];
  generated_recipe: GeneratedRecipe | null;
}

export interface Rating {
  id: string;
  recipe_id: string;
  stars: number;
  notes: string | null;
  would_make_again: boolean | null;
  rated_at: string;
}

export interface RatingCreate {
  recipe_id: string;
  stars: number;
  notes?: string | null;
  would_make_again?: boolean | null;
}

export interface SkippedRow {
  line: string;
  reason: string;
}

export interface BulkImportResult {
  created: PantryItem[];
  warnings: SkippedRow[];
  skipped: SkippedRow[];
}

// --- Food bank feature ---

export interface FoodBankCatalog {
  categories: Record<string, string[]>;
  dietary_flags: string[];
  equipment_constraints: string[];
}

export interface FoodBankGenerateRequest {
  available_items: string[];
  priority_items: string[];
  dietary_flags: string[];
  equipment_constraints: string[];
  card_count: number;
}

export interface RecipeCard {
  title_en: string;
  title_es: string;
  ingredients_en: string[];
  ingredients_es: string[];
  steps_en: string[];
  steps_es: string[];
  dietary_tags: string[];
  uses_priority_items: boolean;
  notes_en: string;
  notes_es: string;
}

export interface FoodBankGenerateResponse {
  cards: RecipeCard[];
  was_mocked: boolean;
}

export interface GenerationLog {
  id: string;
  created_at: string;
  available_items: string[];
  priority_items: string[];
  dietary_flags: string[];
  equipment_constraints: string[];
  card_count_requested: number;
  cards: RecipeCard[];
  was_mocked: boolean;
}
