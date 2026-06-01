function Button({ children, variant = "primary", onClick }) {
  const className = variant === "secondary" ? "secondary-btn" : "primary-btn";

  return (
    <button className={className} onClick={onClick}>
      {children}
    </button>
  );
}

export default Button;