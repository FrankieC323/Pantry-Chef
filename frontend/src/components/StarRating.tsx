import { useState } from "react";

interface StarRatingProps {
  value: number;
  onChange?: (stars: number) => void;
  readOnly?: boolean;
  size?: "sm" | "md";
}

export default function StarRating({ value, onChange, readOnly = false, size = "md" }: StarRatingProps) {
  const [hovered, setHovered] = useState<number | null>(null);
  const displayValue = hovered ?? value;
  const dimension = size === "sm" ? "w-4 h-4" : "w-6 h-6";

  return (
    <div className="flex items-center gap-0.5" role={readOnly ? undefined : "radiogroup"} aria-label="Rating">
      {[1, 2, 3, 4, 5].map((star) => (
        <button
          key={star}
          type="button"
          disabled={readOnly}
          aria-label={`${star} star${star > 1 ? "s" : ""}`}
          aria-checked={value === star}
          role={readOnly ? undefined : "radio"}
          className={readOnly ? "cursor-default" : "cursor-pointer"}
          onMouseEnter={() => !readOnly && setHovered(star)}
          onMouseLeave={() => !readOnly && setHovered(null)}
          onClick={() => !readOnly && onChange?.(star)}
        >
          <svg
            viewBox="0 0 24 24"
            className={`${dimension} transition-colors`}
            fill={star <= displayValue ? "#D4A85A" : "none"}
            stroke={star <= displayValue ? "#B8893D" : "#5C5147"}
            strokeWidth={1.5}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M12 2.5l2.9 6.06 6.6.79-4.86 4.59 1.27 6.56L12 17.27l-5.91 3.23 1.27-6.56L2.5 9.35l6.6-.79L12 2.5z"
            />
          </svg>
        </button>
      ))}
    </div>
  );
}
