import { ChevronDown } from 'lucide-react';
import type { ActivityTypeOption } from '@/types/api';
import { humanizeEnum } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

interface CalendarFiltersProps {
  activityTypes: ActivityTypeOption[];
  selectedCategories: string[];
  selectedActivityTypes: string[];
  onCategoriesChange: (categories: string[]) => void;
  onActivityTypesChange: (types: string[]) => void;
}

export function CalendarFilters({
  activityTypes,
  selectedCategories,
  selectedActivityTypes,
  onCategoriesChange,
  onActivityTypesChange,
}: CalendarFiltersProps) {
  const categories = Array.from(new Set(activityTypes.map((t) => t.category))).sort();

  const toggleCategory = (category: string, checked: boolean) => {
    onCategoriesChange(
      checked
        ? [...selectedCategories, category]
        : selectedCategories.filter((c) => c !== category),
    );
  };

  const toggleActivityType = (value: string, checked: boolean) => {
    onActivityTypesChange(
      checked
        ? [...selectedActivityTypes, value]
        : selectedActivityTypes.filter((t) => t !== value),
    );
  };

  return (
    <div className="flex flex-wrap items-center gap-2">
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="outline" size="sm" className="h-8">
            Category
            {selectedCategories.length > 0 ? ` (${selectedCategories.length})` : ''}
            <ChevronDown className="size-4 opacity-50" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="start" className="w-56">
          <DropdownMenuLabel>Category</DropdownMenuLabel>
          <DropdownMenuSeparator />
          {categories.map((category) => (
            <DropdownMenuCheckboxItem
              key={category}
              checked={selectedCategories.includes(category)}
              onCheckedChange={(checked) => toggleCategory(category, checked === true)}
              onSelect={(e) => e.preventDefault()}
            >
              {humanizeEnum(category)}
            </DropdownMenuCheckboxItem>
          ))}
        </DropdownMenuContent>
      </DropdownMenu>

      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="outline" size="sm" className="h-8">
            Activity type
            {selectedActivityTypes.length > 0 ? ` (${selectedActivityTypes.length})` : ''}
            <ChevronDown className="size-4 opacity-50" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="start" className="w-64 max-h-80 overflow-y-auto">
          <DropdownMenuLabel>Activity type</DropdownMenuLabel>
          <DropdownMenuSeparator />
          {activityTypes.map((type) => (
            <DropdownMenuCheckboxItem
              key={type.value}
              checked={selectedActivityTypes.includes(type.value)}
              onCheckedChange={(checked) => toggleActivityType(type.value, checked === true)}
              onSelect={(e) => e.preventDefault()}
            >
              {type.label}
            </DropdownMenuCheckboxItem>
          ))}
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
}
