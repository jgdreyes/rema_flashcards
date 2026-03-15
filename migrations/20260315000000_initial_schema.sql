-- Migration: 20260315000000_initial_schema
-- Creates user profile and belt/cycle selection tables with RLS policies.

-- Users (extends Supabase auth)
create table public.users (
  id          uuid primary key references auth.users(id) on delete cascade,
  first_name  text,
  last_name   text,
  email       text,
  created_at  timestamptz default now()
);

-- Belt selections
create table public.user_belt_selections (
  user_id   uuid references public.users(id) on delete cascade,
  belt_key  text,
  primary key (user_id, belt_key)
);

-- Cycle selections
create table public.user_cycle_selections (
  user_id    uuid references public.users(id) on delete cascade,
  cycle_key  text,
  primary key (user_id, cycle_key)
);

-- Row Level Security: users can only see/edit their own data
alter table public.users                 enable row level security;
alter table public.user_belt_selections  enable row level security;
alter table public.user_cycle_selections enable row level security;

create policy "users: own row only" on public.users
  for all using (auth.uid() = id);

create policy "belt_selections: own rows only" on public.user_belt_selections
  for all using (auth.uid() = user_id);

create policy "cycle_selections: own rows only" on public.user_cycle_selections
  for all using (auth.uid() = user_id);