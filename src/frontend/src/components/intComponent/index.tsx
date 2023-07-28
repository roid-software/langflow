import { useEffect } from "react";
import { FloatComponentType } from "../../types/components";
import { Input } from "../ui/input";

export default function IntComponent({
  value,
  onChange,
  disabled,
  editNode = false,
}: FloatComponentType) {
  const min = 0;

  // Clear component state
  useEffect(() => {
    if (disabled) {
      onChange("");
    }
  }, [disabled, onChange]);

  const handleKeyDown = (e: React.ChangeEvent<HTMLInputElement>) => {
    
    if (e.ctrlKey && value === '0' && e.key === "Backspace") {
      e.preventDefault();
      e.stopPropagation();
    }
  };

  return (
    <div className="w-full">
      <Input
        onKeyDown={(event) => {
          if (
            event.key !== "Backspace" &&
            event.key !== "Enter" &&
            event.key !== "Delete" &&
            event.key !== "ArrowLeft" &&
            event.key !== "ArrowRight" &&
            event.key !== "Control" &&
            event.key !== "Meta" &&
            event.key !== "Shift" &&
            event.key !== "c" &&
            event.key !== "v" &&
            event.key !== "a" &&
            !/^[-]?\d*$/.test(event.key)
          ) {
            event.preventDefault();
          }
        }}
        type="number"
        step="1"
        min={min}
        onInput={(e: React.ChangeEvent<HTMLInputElement>) => {
          if (e.target.value < min.toString()) {
            e.target.value = min.toString();
          }
        }}
        value={value ?? ""}
        className={editNode ? "input-edit-node" : ""}
        disabled={disabled}
        placeholder={editNode ? "Integer number" : "Type an integer number"}
        onChange={(e) => {
          onChange(e.target.value);
        }}
        onKeyDown={handleKeyDown}
      />
    </div>
  );
}
