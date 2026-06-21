-- CivicRadar — migrate report photos from text data URLs to Supabase Storage
-- Run when you outgrow the free-tier DB (images in `reports.image` text column).
-- See ARCHITECTURE.md Stage 1 for the full rollout plan.
--
-- Prerequisites:
--   1. Create bucket `report-photos` (public read, authenticated write) in Storage
--   2. Deploy app build that uploads to Storage and stores URL in `image_url`
--   3. Run this SQL once, then run a one-off migration script to move existing blobs

-- ---------------------------------------------------------------------
-- Schema changes
-- ---------------------------------------------------------------------

alter table public.reports add column if not exists image_url text;

comment on column public.reports.image is 'Legacy: JPEG data URL (MVP). Null after Storage migration.';
comment on column public.reports.image_url is 'Public URL to object in report-photos bucket.';

-- ---------------------------------------------------------------------
-- Storage bucket (adjust policies for your threat model)
-- ---------------------------------------------------------------------

insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values (
  'report-photos',
  'report-photos',
  true,
  524288,  -- 512 KB per object after client compression
  array['image/jpeg', 'image/webp']
)
on conflict (id) do nothing;

-- Anyone can view hazard photos (public map).
drop policy if exists "report_photos_select" on storage.objects;
create policy "report_photos_select"
  on storage.objects for select
  using (bucket_id = 'report-photos');

-- Authenticated users upload only into their own folder: {user_id}/{report_id}.jpg
drop policy if exists "report_photos_insert_own" on storage.objects;
create policy "report_photos_insert_own"
  on storage.objects for insert
  to authenticated
  with check (
    bucket_id = 'report-photos'
    and (storage.foldername(name))[1] = auth.uid()::text
  );

drop policy if exists "report_photos_update_own" on storage.objects;
create policy "report_photos_update_own"
  on storage.objects for update
  to authenticated
  using (
    bucket_id = 'report-photos'
    and (storage.foldername(name))[1] = auth.uid()::text
  );

drop policy if exists "report_photos_delete_own" on storage.objects;
create policy "report_photos_delete_own"
  on storage.objects for delete
  to authenticated
  using (
    bucket_id = 'report-photos'
    and (storage.foldername(name))[1] = auth.uid()::text
  );

-- ---------------------------------------------------------------------
-- Optional: backfill helper (run from Edge Function or admin script, not inline)
-- ---------------------------------------------------------------------
-- For each row where image is not null and image_url is null:
--   1. decode data URL → upload to report-photos/{reporter_id}/{id}.jpg
--   2. update reports set image_url = public_url, image = null where id = ...
