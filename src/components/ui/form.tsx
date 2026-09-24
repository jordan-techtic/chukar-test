import * as LabelPrimitive from "@radix-ui/react-label";
import { Slot } from "@radix-ui/react-slot";
import {
  createContext,
  useContext,
  useId,
  type ComponentProps,
  type HTMLAttributes,
} from "react";
import {
  Controller,
  FormProvider,
  useFormContext,
  type ControllerProps,
  type FieldPath,
  type FieldValues,
} from "react-hook-form";
import { cn } from "@/lib/cn";
import { Label } from "@/components/ui/label";

export const Form = FormProvider;

type FormFieldContextValue<
  TFieldValues extends FieldValues = FieldValues,
  TName extends FieldPath<TFieldValues> = FieldPath<TFieldValues>,
> = {
  name: TName;
};

const FormFieldContext = createContext<FormFieldContextValue | undefined>(undefined);

export function FormField<
  TFieldValues extends FieldValues = FieldValues,
  TName extends FieldPath<TFieldValues> = FieldPath<TFieldValues>,
>({ ...props }: ControllerProps<TFieldValues, TName>) {
  return (
    <FormFieldContext.Provider value={{ name: props.name }}>
      <Controller {...props} />
    </FormFieldContext.Provider>
  );
}

type FormItemContextValue = { id: string };
const FormItemContext = createContext<FormItemContextValue | undefined>(undefined);

export function FormItem({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  const id = useId();
  return (
    <FormItemContext.Provider value={{ id }}>
      <div className={cn("space-y-1.5", className)} {...props} />
    </FormItemContext.Provider>
  );
}

function useFormField() {
  const fieldContext = useContext(FormFieldContext);
  const itemContext = useContext(FormItemContext);
  const { getFieldState, formState } = useFormContext();
  if (!fieldContext || !itemContext) {
    throw new Error("Form components must be used within FormField and FormItem");
  }
  const fieldState = getFieldState(fieldContext.name, formState);
  return {
    id: itemContext.id,
    name: fieldContext.name,
    formItemId: `${itemContext.id}-form-item`,
    formDescriptionId: `${itemContext.id}-form-description`,
    formMessageId: `${itemContext.id}-form-message`,
    ...fieldState,
  };
}

export function FormLabel({
  className,
  htmlFor,
  ...props
}: ComponentProps<typeof LabelPrimitive.Root>) {
  const { error, formItemId } = useFormField();
  return (
    <Label className={cn(error && "text-destructive", className)} htmlFor={htmlFor ?? formItemId} {...props} />
  );
}

export function FormControl({ ...props }: ComponentProps<typeof Slot>) {
  const { error, formItemId, formDescriptionId, formMessageId } = useFormField();
  return (
    <Slot
      id={formItemId}
      aria-describedby={error ? `${formDescriptionId} ${formMessageId}` : formDescriptionId}
      aria-invalid={error ? true : undefined}
      {...props}
    />
  );
}

export function FormDescription({ className, ...props }: HTMLAttributes<HTMLParagraphElement>) {
  const { formDescriptionId } = useFormField();
  return (
    <p id={formDescriptionId} className={cn("text-sm text-muted-foreground", className)} {...props} />
  );
}

export function FormMessage({ className, children, ...props }: HTMLAttributes<HTMLParagraphElement>) {
  const { error, formMessageId } = useFormField();
  const body = error ? String(error.message ?? "") : children;
  if (!body) return null;
  return (
    <p id={formMessageId} role="alert" className={cn("text-sm text-destructive", className)} {...props}>
      {body}
    </p>
  );
}
