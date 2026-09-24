import type { Control } from 'react-hook-form';
import type { ActivityTypeOption } from '@/types/api';
import { Input } from '@/components/ui/input';
import { DatePicker } from '@/components/ui/date-picker';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import type { ActivityFormValues } from './activityFormSchema';

interface ActivityFormFieldsProps {
  control: Control<ActivityFormValues>;
  activityTypes: ActivityTypeOption[];
  selectedType?: ActivityTypeOption;
  onActivityTypeChange: (value: string) => void;
}

export function ActivityFormFields({
  control,
  activityTypes,
  selectedType,
  onActivityTypeChange,
}: ActivityFormFieldsProps) {
  return (
    <div className="space-y-4">
      <FormField
        control={control}
        name="title"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Title</FormLabel>
            <FormControl>
              <Input placeholder="Activity title" {...field} />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />

      <div className="grid gap-4 sm:grid-cols-2">
        <FormField
          control={control}
          name="start_date"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Start date</FormLabel>
              <FormControl>
                <DatePicker
                  value={field.value}
                  onChange={field.onChange}
                  placeholder="Pick start date"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={control}
          name="end_date"
          render={({ field }) => (
            <FormItem>
              <FormLabel>End date (optional)</FormLabel>
              <FormControl>
                <DatePicker
                  value={field.value ?? ''}
                  onChange={field.onChange}
                  placeholder="Pick end date"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
      </div>

      <FormField
        control={control}
        name="activity_type"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Activity type</FormLabel>
            <Select
              value={field.value}
              onValueChange={(value) => {
                field.onChange(value);
                onActivityTypeChange(value);
              }}
            >
              <FormControl>
                <SelectTrigger>
                  <SelectValue placeholder="Select activity type" />
                </SelectTrigger>
              </FormControl>
              <SelectContent>
                {activityTypes.map((type) => (
                  <SelectItem key={type.value} value={type.value}>
                    {type.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <FormMessage />
          </FormItem>
        )}
      />

      <FormField
        control={control}
        name="details"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Details</FormLabel>
            <FormControl>
              <Textarea placeholder="Activity details" rows={3} {...field} value={field.value ?? ''} />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />

      {selectedType?.fields.map((dynamicField) => (
        <FormField
          key={dynamicField.name}
          control={control}
          name="additional_info"
          render={({ field }) => (
            <FormItem>
              <FormLabel>{dynamicField.label}</FormLabel>
              <FormControl>
                <Textarea
                  placeholder={dynamicField.label}
                  rows={2}
                  maxLength={dynamicField.max_length}
                  {...field}
                  value={field.value ?? ''}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
      ))}
    </div>
  );
}
