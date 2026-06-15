import { useLayoutEffect, useRef } from "react";
import type { ChangeEvent, TextareaHTMLAttributes } from "react";

type AutoResizeTextareaProps = TextareaHTMLAttributes<HTMLTextAreaElement>;

export function AutoResizeTextarea({ onChange, value, ...props }: AutoResizeTextareaProps) {
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);

  function resize() {
    const textarea = textareaRef.current;
    if (!textarea) return;
    textarea.style.height = "auto";
    textarea.style.height = `${textarea.scrollHeight}px`;
  }

  useLayoutEffect(() => {
    resize();
  }, [value]);

  function handleChange(event: ChangeEvent<HTMLTextAreaElement>) {
    onChange?.(event);
    requestAnimationFrame(resize);
  }

  return <textarea {...props} ref={textareaRef} value={value} onChange={handleChange} />;
}
