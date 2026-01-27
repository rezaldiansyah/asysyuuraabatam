"use client"

import * as React from "react"
import {
    BookOpen,
    Frame,
    LifeBuoy,
    Map,
    PieChart,
    School,
    Send,
    Settings2,
    SquareTerminal,
    User,
    Users,
    ChevronRight,
    CircleDollarSign,
} from "lucide-react"

import {
    Sidebar,
    SidebarContent,
    SidebarFooter,
    SidebarHeader,
    SidebarMenu,
    SidebarMenuButton,
    SidebarMenuItem,
    SidebarRail,
    SidebarGroup,
    SidebarGroupLabel,
    SidebarGroupContent,
    SidebarMenuSub,
    SidebarMenuSubButton,
    SidebarMenuSubItem,
} from "@/components/ui/sidebar"
import { Separator } from "@/components/ui/separator"
import { NavUser } from "./NavUser"
import {
    Collapsible,
    CollapsibleContent,
    CollapsibleTrigger,
} from "@/components/ui/collapsible"

const data = {
    user: {
        name: "Administrator",
        email: "admin@asysyuura.sch.id",
        avatar: "/avatars/shadcn.jpg",
    },
    navMain: [
        {
            title: "Dashboard",
            url: "/dashboard",
            icon: SquareTerminal,
            isActive: true,
        },
        {
            title: "Akademik",
            url: "#",
            icon: BookOpen,
            items: [
                {
                    title: "Data Siswa",
                    url: "/dashboard/siswa",
                },
                {
                    title: "Data Guru",
                    url: "/dashboard/guru",
                },
                {
                    title: "Jadwal Pelajaran",
                    url: "/dashboard/jadwal",
                },
            ],
        },
        {
            title: "Keuangan",
            url: "#",
            icon: CircleDollarSign,
            items: [
                {
                    title: "SPP & Tagihan",
                    url: "/dashboard/keuangan",
                },
            ]
        },
        {
            title: "CMS Website",
            url: "#",
            icon: Send, // Using Send as a placeholder for Publish/CMS
            items: [
                {
                    title: "Konten Landing Page",
                    url: "/dashboard/cms/konten",
                },
                {
                    title: "Berita Sekolah",
                    url: "/dashboard/cms/berita",
                },
            ],
        },
        {
            title: "Settings",
            url: "#",
            icon: Settings2,
            items: [
                {
                    title: "Manajemen User",
                    url: "#",
                },
                {
                    title: "Konfigurasi Sekolah",
                    url: "#",
                },
            ],
        },
    ],
}

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
    return (
        <Sidebar collapsible="icon" {...props}>
            <SidebarHeader>
                <div className="flex items-center gap-2 px-2 py-2">
                    <div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-[var(--syuura-green)] text-sidebar-primary-foreground">
                        <School className="size-4 text-white" />
                    </div>
                    <div className="grid flex-1 text-left text-sm leading-tight">
                        <span className="truncate font-semibold text-[var(--syuura-green)]">Asy-Syuuraa</span>
                        <span className="truncate text-xs text-slate-500">Sistem Informasi</span>
                    </div>
                </div>
            </SidebarHeader>
            <Separator className="my-2 bg-slate-100" />
            <SidebarContent>
                {/* Generik Navigation */}
                <SidebarGroup>
                    <SidebarGroupLabel>Menu Utama</SidebarGroupLabel>
                    <SidebarGroupContent>
                        <SidebarMenu>
                            {data.navMain.map((item) => (
                                item.items?.length ? (
                                    <Collapsible
                                        key={item.title}
                                        asChild
                                        defaultOpen={item.isActive}
                                        className="group/collapsible"
                                    >
                                        <SidebarMenuItem>
                                            <CollapsibleTrigger asChild>
                                                <SidebarMenuButton tooltip={item.title}>
                                                    {item.icon && <item.icon />}
                                                    <span>{item.title}</span>
                                                    <ChevronRight className="ml-auto transition-transform duration-200 group-data-[state=open]/collapsible:rotate-90" />
                                                </SidebarMenuButton>
                                            </CollapsibleTrigger>
                                            <CollapsibleContent>
                                                <SidebarMenuSub>
                                                    {item.items?.map((subItem) => (
                                                        <SidebarMenuSubItem key={subItem.title}>
                                                            <SidebarMenuSubButton asChild>
                                                                <a href={subItem.url}>
                                                                    <span>{subItem.title}</span>
                                                                </a>
                                                            </SidebarMenuSubButton>
                                                        </SidebarMenuSubItem>
                                                    ))}
                                                </SidebarMenuSub>
                                            </CollapsibleContent>
                                        </SidebarMenuItem>
                                    </Collapsible>
                                ) : (
                                    <SidebarMenuItem key={item.title}>
                                        <SidebarMenuButton tooltip={item.title} asChild>
                                            <a href={item.url}>
                                                {item.icon && <item.icon />}
                                                <span>{item.title}</span>
                                            </a>
                                        </SidebarMenuButton>
                                    </SidebarMenuItem>
                                )
                            ))}
                        </SidebarMenu>
                    </SidebarGroupContent>
                </SidebarGroup>
            </SidebarContent>
            <SidebarFooter>
                <NavUser user={data.user} />
            </SidebarFooter>
            <SidebarRail />
        </Sidebar>
    )
}
