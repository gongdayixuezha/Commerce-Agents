import "./globals.css";

export const metadata = {
  title: "Commerce Agent - AI 电商助手",
  description: "AI 驱动的电商购物助手，搜索、对比、一键购买",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body className="bg-gray-50 min-h-screen">{children}</body>
    </html>
  );
}
