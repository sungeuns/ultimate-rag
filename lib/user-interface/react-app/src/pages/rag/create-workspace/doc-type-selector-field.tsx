import {
  FormField,
  Select,
  SelectProps,
} from "@cloudscape-design/components";


interface DocTypeSelectorProps {
  submitting: boolean;
  onChange: (data: Partial<{ docType: SelectProps.Option }>) => void;
  docType: SelectProps.Option | null;
  errors: Record<string, string | string[]>;
}

export function DocTypeSelectorField(props: DocTypeSelectorProps) {

  const docTypeList = [
    {value: "NORMAL", label: "Normal"},
    {value: "COMPLEX", label: "Complex"},
  ]

  return (
    <FormField label="Document type" errorText={props.errors.docType}>
      <Select
        disabled={props.submitting}
        selectedAriaLabel="Selected"
        placeholder="Choose an document type"
        // statusType={embeddingsModelsStatus}
        // loadingText="Loading embeddings models (might take few seconds)..."
        selectedOption={props.docType}
        options={docTypeList}
        onChange={({ detail: { selectedOption } }) =>
          props.onChange({ docType: selectedOption })
        }
      />
    </FormField>
  );
}
