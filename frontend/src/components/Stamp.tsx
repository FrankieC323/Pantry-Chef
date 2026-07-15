interface StampProps {
  children: React.ReactNode;
  variant?: "urgent" | "warm" | "neutral";
}

const variantStyles: Record<NonNullable<StampProps["variant"]>, string> = {
  urgent: "border-terracotta-500 text-terracotta-600 bg-terracotta-400/10",
  warm: "border-gold-500 text-gold-600 bg-gold-400/10",
  neutral: "border-cookbook-600 text-cookbook-700 bg-cookbook-50",
};

export default function Stamp({ children, variant = "neutral" }: StampProps) {
  return <span className={`stamp ${variantStyles[variant]}`}>{children}</span>;
}
