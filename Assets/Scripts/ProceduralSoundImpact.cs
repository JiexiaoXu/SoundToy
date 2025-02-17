using UnityEngine;

public class ProceduralSoundImpact : MonoBehaviour
{
    private AudioSource audioSource;
    private float frequency = 440f; 
    private float amplitude = 0.0f; 
    private float decayRate = 0.005f; 
    private float sampleRate = 48000f; 
    private float phase = 0f;

    void Start()
    {
        // Get or create AudioSource
        audioSource = GetComponent<AudioSource>();
        if (audioSource == null)
            audioSource = gameObject.AddComponent<AudioSource>();

        // Ensure AudioSource is playing so OnAudioFilterRead() runs
        audioSource.loop = true;
        audioSource.playOnAwake = false;
        audioSource.spatialBlend = 1; 
        audioSource.volume = 1.0f;
        audioSource.Play();
    }

    void OnCollisionEnter(Collision collision)
    {
        // Generate a random frequency for each collision
        float impactForce = collision.relativeVelocity.magnitude;

        if (impactForce > 0.5f) // Ensure weak collisions don't trigger sound
        {
            frequency = Mathf.Lerp(200, 1000, impactForce / 10f); // Impact pitch
            amplitude = Mathf.Clamp(impactForce / 10f, 0f, 1f);
        }
    }

    void OnAudioFilterRead(float[] data, int channels)
    {
        if (amplitude <= 0 || this == null) return;
        for (int i = 0; i < data.Length; i += channels)
        {
            // Generate sine wave
            phase += 2.0f * Mathf.PI * frequency / sampleRate;
            if (phase > Mathf.PI * 2) phase -= Mathf.PI * 2;

            float sample = Mathf.Sin(phase) * amplitude;
            amplitude -= decayRate;
            if (amplitude < 0) amplitude = 0;

            // Apply sample to all audio channels
            for (int j = 0; j < channels; j++)
                data[i + j] = sample;
        }
    }
}
