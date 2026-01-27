import { Star, CheckCircle, BookOpen, Heart, Sun, Users, Trophy, ShieldCheck, Sparkles } from "lucide-react";

interface FeatureItem {
    id: string;
    title: string;
    description: string;
    image_url?: string;
    icon?: string;
}

interface DynamicFeatureSectionProps {
    title?: string;
    subtitle?: string;
    features: FeatureItem[];
}

const ICON_MAP: Record<string, any> = {
    BookOpen, Heart, Sun, Users, Trophy, ShieldCheck, Star, Sparkles, CheckCircle
};

export function DynamicFeatureSection({ title = "Keunggulan Kami", subtitle, features }: DynamicFeatureSectionProps) {
    if (!features || features.length === 0) return null;

    return (
        <section className="py-20 bg-slate-50">
            <div className="container mx-auto px-4">
                <div className="text-center mb-16">
                    <h2 className="text-3xl font-bold text-[var(--syuura-green)] mb-2">{title}</h2>
                    {subtitle && <p className="text-slate-500">{subtitle}</p>}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-x-8 gap-y-12">
                    {features.map((feature, idx) => (
                        <div key={idx} className="flex gap-4 items-start">
                            <div className="p-3 bg-white rounded-lg shadow-sm text-[var(--syuura-gold)] shrink-0">
                                {/* Use image if available, else use Icon */}
                                {feature.image_url ? (
                                    <img src={feature.image_url} alt="" className="h-8 w-8 object-contain" />
                                ) : (
                                    (() => {
                                        const IconComponent = ICON_MAP[feature.icon || "CheckCircle"] || CheckCircle;
                                        return <IconComponent className="h-8 w-8" />;
                                    })()
                                )}
                            </div>
                            <div>
                                <h3 className="text-lg font-bold text-slate-800 mb-2">{feature.title}</h3>
                                <p className="text-sm text-slate-600 leading-relaxed">{feature.description}</p>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
}
