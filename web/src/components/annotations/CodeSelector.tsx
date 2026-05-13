import { Input } from "@/components/ui/Form";

interface Props {
  value: string;
  onChange: (v: string) => void;
}

export function CodeSelector({ value, onChange }: Props) {
  return <Input value={value} onChange={(e) => onChange(e.target.value)} placeholder="code id from codebook" />;
}
